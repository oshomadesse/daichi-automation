"""proposals.json から見積計算→PDF→Drive→Sheets→メールまでを一括実行する。

企画案の生成は Claude Code が担当し、このスクリプトは後続の処理を自動化する。
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path

import config


def _run_id(source_name: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{ts}_{source_name}"


def _state_path(run_dir: str) -> str:
    return os.path.join(run_dir, "state.json")


def _load_state(run_dir: str) -> dict:
    sp = _state_path(run_dir)
    if os.path.exists(sp):
        with open(sp) as f:
            return json.load(f)
    return {}


def _save_state(run_dir: str, state: dict):
    with open(_state_path(run_dir), "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _step(label: str, step_num: int, total: int):
    print(f"[{step_num}/{total}] {label}...", end=" ", flush=True)


def _ok(start: float):
    elapsed = time.time() - start
    if elapsed >= 1:
        print(f"OK ({elapsed:.0f}s)")
    else:
        print("OK")


def _find_existing_run(source_name: str) -> str | None:
    if not os.path.exists(config.RUNS_DIR):
        return None
    for d in sorted(os.listdir(config.RUNS_DIR), reverse=True):
        if source_name in d:
            run_dir = os.path.join(config.RUNS_DIR, d)
            if os.path.isdir(run_dir) and os.path.exists(_state_path(run_dir)):
                return run_dir
    return None


def run_pipeline(proposals_path: str, source_name: str = "", resume: bool = False, dry_run: bool = False):
    from pipeline.google_sheets import read_rate_table, append_result_row
    from pipeline.estimate import calculate_estimate
    from pipeline.pdf_report import generate_pdf
    from pipeline.google_docs import create_proposal_doc
    from pipeline.google_drive import upload_pdf
    from pipeline.notify import send_notification

    total = 6
    proposals_path = os.path.abspath(proposals_path)

    if not source_name:
        source_name = Path(proposals_path).stem

    # Load proposals
    with open(proposals_path) as f:
        proposals = json.load(f)
    print(f"企画案読込: {proposals_path} ({len(proposals.get('proposals', []))}件)")

    # Setup run directory
    if resume:
        run_dir = _find_existing_run(source_name)
        if not run_dir:
            print("再開可能な実行が見つかりません。新規実行します。")
            resume = False

    if not resume:
        rid = _run_id(source_name)
        run_dir = os.path.join(config.RUNS_DIR, rid)
        os.makedirs(run_dir, exist_ok=True)

    state = _load_state(run_dir) if resume else {
        "run_id": os.path.basename(run_dir),
        "proposals_path": proposals_path,
        "source_name": source_name,
        "steps_completed": [],
    }
    done = set(state.get("steps_completed", []))

    # Step 1: Read rate table
    if "read_rates" not in done:
        _step("単価テーブル読込中", 1, total)
        t = time.time()
        rate_table = read_rate_table()
        state["rate_table"] = rate_table
        done.add("read_rates")
        state["steps_completed"] = list(done)
        _save_state(run_dir, state)
        _ok(t)
    else:
        print(f"[1/{total}] 単価テーブル読込中... SKIP (済)")
        rate_table = state["rate_table"]

    # Step 2: Calculate estimate
    if "estimate" not in done:
        _step("見積り計算中", 2, total)
        t = time.time()
        estimates = calculate_estimate(proposals, rate_table)
        estimates_path = os.path.join(run_dir, "estimates.json")
        with open(estimates_path, "w") as f:
            json.dump(estimates, f, ensure_ascii=False, indent=2)
        state["estimates_path"] = estimates_path
        done.add("estimate")
        state["steps_completed"] = list(done)
        _save_state(run_dir, state)
        _ok(t)
    else:
        print(f"[2/{total}] 見積り計算中... SKIP (済)")
        with open(state["estimates_path"]) as f:
            estimates = json.load(f)

    # Step 3: Generate PDF
    if "pdf" not in done:
        _step("見積書PDF生成中", 3, total)
        t = time.time()
        pdf_path = os.path.join(run_dir, "estimate.pdf")
        generate_pdf(estimates, pdf_path)
        state["pdf_path"] = pdf_path
        done.add("pdf")
        state["steps_completed"] = list(done)
        _save_state(run_dir, state)
        _ok(t)
    else:
        print(f"[3/{total}] 見積書PDF生成中... SKIP (済)")
        pdf_path = state["pdf_path"]

    if dry_run:
        print(f"\n[DRY RUN] アップロード・メール送信をスキップしました。")
        print(f"  見積書PDF: {pdf_path}")
        return

    # Step 4: Upload to Drive / Create Google Doc
    if "upload" not in done:
        _step("Drive/Docsアップロード中", 4, total)
        t = time.time()
        proposal_url = create_proposal_doc(proposals, source_name)
        pdf_url = upload_pdf(pdf_path, f"見積書_{source_name}.pdf")
        state["proposal_url"] = proposal_url
        state["pdf_url"] = pdf_url
        done.add("upload")
        state["steps_completed"] = list(done)
        _save_state(run_dir, state)
        _ok(t)
    else:
        print(f"[4/{total}] Drive/Docsアップロード中... SKIP (済)")
        proposal_url = state["proposal_url"]
        pdf_url = state["pdf_url"]

    # Step 5: Update spreadsheet
    if "sheet" not in done:
        _step("スプレッドシート更新中", 5, total)
        t = time.time()
        append_result_row(source_name, proposal_url, pdf_url)
        done.add("sheet")
        state["steps_completed"] = list(done)
        _save_state(run_dir, state)
        _ok(t)
    else:
        print(f"[5/{total}] スプレッドシート更新中... SKIP (済)")

    # Step 6: Send notification
    if "notify" not in done:
        _step("メール送信中", 6, total)
        t = time.time()
        send_notification(source_name, proposal_url, pdf_url)
        done.add("notify")
        state["steps_completed"] = list(done)
        _save_state(run_dir, state)
        _ok(t)
    else:
        print(f"[6/{total}] メール送信中... SKIP (済)")

    print(f"\n✅ 完了！")
    print(f"  企画案: {proposal_url}")
    print(f"  見積書: {pdf_url}")
