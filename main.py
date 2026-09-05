"""
NovelNexus Recommendation Pipeline Orchestrator.

Complete End-to-End MLOps Pipeline with Stage and Individual Step Support:

Run by Stage:
  python main.py                           # Run full pipeline (Steps 1-9)
  python main.py --stage all               # Run full pipeline (Steps 1-9)
  python main.py --stage ingest            # Step 1: Ingestion
  python main.py --stage preprocess        # Steps 2-4: Data Cleaning, Users, Books
  python main.py --stage recommend         # Steps 5-8: Demographic, Geo, SVD, & Similarity
  python main.py --stage aggregate         # Step 9: Multi-model Combined Aggregator

Run by Exact Step:
  python main.py --step 1                  # Ingestion only
  python main.py --step 2                  # Preprocess raw data only
  python main.py --step 7                  # Collaborative SVD + KMeans only
  python main.py --step 8                  # Item-item similarity only
  python main.py --step 9                  # Combine recommendations only
"""
import sys
import time
import argparse
from typing import Callable, Dict, List, Tuple
from config.logging_configs import logger

# Pipeline Step Modules
from src.data_inject import fetch_raw_data
from src.data_preprocessing import preprocessing_raw_data, users, books
from src.recommender.demographic_recommender import age_group_recommender
from src.recommender.geographic_recommender import geo_locational_recommender
from src.recommender.collaborative_filtering_recommender import recommended_for_you
from src.recommender.collaborative_filtering_recommender import people_also_read
from src.recommender.user_combined_recommendation import user_combined_recommendation

# Registry of all pipeline steps in strict dependency order (1 to 9)
STEPS_REGISTRY: Dict[int, Dict[str, any]] = {
    1: {
        "alias": "ingest",
        "stage": "Ingestion",
        "title": "Ingest Raw Datasets (Google Drive / Local Fallback)",
        "func": fetch_raw_data.main,
    },
    2: {
        "alias": "preprocess",
        "stage": "Preprocessing",
        "title": "Clean & Filter Raw Ratings/Books (Vectorized)",
        "func": preprocessing_raw_data.main,
    },
    3: {
        "alias": "users",
        "stage": "Preprocessing",
        "title": "Extract Distinct User Demographic Profiles",
        "func": users.main,
    },
    4: {
        "alias": "books",
        "stage": "Preprocessing",
        "title": "Extract Distinct Book Catalog Records",
        "func": books.main,
    },
    5: {
        "alias": "demographic",
        "stage": "Recommender",
        "title": "Demographic Age-Bracket Recommendation Engine",
        "func": age_group_recommender.main,
    },
    6: {
        "alias": "geographic",
        "stage": "Recommender",
        "title": "Geographic Locational Recommendation Engine",
        "func": geo_locational_recommender.main,
    },
    7: {
        "alias": "svd",
        "stage": "Recommender",
        "title": "Collaborative Filtering (TruncatedSVD + MiniBatchKMeans)",
        "func": recommended_for_you.main,
    },
    8: {
        "alias": "similarity",
        "stage": "Recommender",
        "title": "Item-to-Item Cosine Similarity (People Also Read)",
        "func": people_also_read.main,
    },
    9: {
        "alias": "aggregate",
        "stage": "Aggregation",
        "title": "Multi-Model Combined Recommendation Aggregator",
        "func": user_combined_recommendation.main,
    },
}

STAGE_MAPPING: Dict[str, List[int]] = {
    "all": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "ingest": [1],
    "preprocess": [2, 3, 4],
    "recommend": [5, 6, 7, 8],
    "aggregate": [9],
}

STEP_ALIASES: Dict[str, int] = {
    "1": 1, "ingest": 1,
    "2": 2, "preprocess": 2, "clean": 2,
    "3": 3, "users": 3,
    "4": 4, "books": 4,
    "5": 5, "demographic": 5, "age": 5,
    "6": 6, "geographic": 6, "geo": 6, "location": 6,
    "7": 7, "svd": 7, "collaborative": 7, "clusters": 7,
    "8": 8, "similarity": 8, "cosine": 8, "also_read": 8,
    "9": 9, "aggregate": 9, "combined": 9,
}


def log_banner(message: str, char: str = "="):
    """Outputs a clean, centered log header banner."""
    line = char * 80
    logger.info(line)
    logger.info(f"  {message}")
    logger.info(line)


def run_step(step_num: int) -> Tuple[bool, float]:
    """Executes a single registered pipeline step with profiling."""
    info = STEPS_REGISTRY[step_num]
    stage_name = info["stage"].upper()
    title = info["title"]
    func = info["func"]

    logger.info("")
    log_banner(f"[STEP {step_num}/9] [{stage_name}] {title}", "-")
    start_time = time.time()
    try:
        func()
        duration = time.time() - start_time
        logger.info(f"--> [SUCCESS] Step {step_num} finished in {duration:.2f}s")
        return True, duration
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"--> [FAILED] Step {step_num} failed after {duration:.2f}s: {e}")
        return False, duration


def print_summary_table(results: List[Dict[str, any]], total_elapsed: float):
    """Prints a structured MLOps summary report."""
    logger.info("")
    log_banner("NOVELNEXUS PIPELINE EXECUTION SUMMARY")
    logger.info(f"{'Step':<6} {'Stage':<14} {'Task Title':<42} {'Status':<10} {'Runtime':<8}")
    logger.info("-" * 84)

    all_passed = True
    for item in results:
        status_str = "SUCCESS" if item["success"] else "FAILED"
        if not item["success"]:
            all_passed = False
        logger.info(
            f"{item['step']:<6} {item['stage']:<14} {item['title'][:40]:<42} {status_str:<10} {item['duration']:.2f}s"
        )

    logger.info("-" * 84)
    overall_status = "ALL STEPS COMPLETED SUCCESSFULLY" if all_passed else "SOME STEPS ENCOUNTERED ERRORS"
    logger.info(f"TOTAL PIPELINE DURATION: {total_elapsed:.2f}s | Result: {overall_status}")
    logger.info("=" * 84)
    logger.info("")


def parse_args():
    parser = argparse.ArgumentParser(
        description="NovelNexus Book Recommender Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                      # Execute complete pipeline (Steps 1-9)
  python main.py --stage preprocess   # Execute Steps 2, 3, 4
  python main.py --stage recommend    # Execute Steps 5, 6, 7, 8
  python main.py --step 7             # Execute Collaborative SVD + KMeans only
  python main.py --step similarity    # Execute Item-Item Cosine Similarity only
        """
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--stage",
        type=str,
        choices=["all", "ingest", "preprocess", "recommend", "aggregate"],
        default="all",
        help="Run an entire stage group of steps (default: all)"
    )
    group.add_argument(
        "--step",
        type=str,
        help="Run a specific individual step by number (1-9) or alias (e.g. 'svd', 'users', 'similarity')"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    overall_start = time.time()

    # Determine which steps to run
    if args.step:
        step_key = str(args.step).strip().lower()
        if step_key not in STEP_ALIASES:
            logger.error(
                f"Invalid step '{args.step}'. Supported steps: 1-9, or aliases: "
                f"{', '.join(sorted(set(STEP_ALIASES.keys())))}"
            )
            sys.exit(1)
        target_steps = [STEP_ALIASES[step_key]]
        execution_mode = f"Single Step ({target_steps[0]}: {STEPS_REGISTRY[target_steps[0]]['title']})"
    else:
        target_steps = STAGE_MAPPING[args.stage]
        execution_mode = f"Stage '{args.stage}' ({len(target_steps)} steps)"

    logger.info("")
    log_banner(f"STARTING NOVELNEXUS PIPELINE | Mode: {execution_mode}")
    logger.info(f"Executing Steps: {target_steps}")

    execution_records = []
    for step_num in target_steps:
        success, duration = run_step(step_num)
        execution_records.append({
            "step": step_num,
            "stage": STEPS_REGISTRY[step_num]["stage"],
            "title": STEPS_REGISTRY[step_num]["title"],
            "success": success,
            "duration": duration,
        })
        if not success:
            logger.error(f"Terminating pipeline due to failure at step {step_num}.")
            break

    total_time = time.time() - overall_start
    print_summary_table(execution_records, total_time)


if __name__ == "__main__":
    main()
