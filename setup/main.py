import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="proposals.jsonから見積書PDF生成→Drive/スプシ/メールまで一括処理"
    )
    parser.add_argument("proposals_json", help="企画案JSONファイルのパス")
    parser.add_argument("--name", default="", help="案件名 (省略時はファイル名から自動設定)")
    parser.add_argument("--resume", action="store_true", help="前回の途中から再開")
    parser.add_argument("--dry-run", action="store_true", help="アップロード・メール送信をスキップ")
    args = parser.parse_args()

    from pipeline.runner import run_pipeline

    try:
        run_pipeline(args.proposals_json, source_name=args.name, resume=args.resume, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n中断されました。--resume で再開できます。")
        sys.exit(1)
    except Exception as e:
        print(f"\nエラー: {e}")
        print("--resume で途中から再開できます。")
        sys.exit(1)


if __name__ == "__main__":
    main()
