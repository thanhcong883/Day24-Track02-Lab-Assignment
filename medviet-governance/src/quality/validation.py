# src/quality/validation.py
import pandas as pd


def build_patient_expectation_suite() -> dict:
    """
    Tạo expectation suite cho patient data.
    Trả về dict mô tả các expectation (không cần GX context file-based).
    """
    try:
        import great_expectations as gx
        context = gx.get_context()
        suite = context.add_expectation_suite("patient_data_suite")

        df = pd.read_csv("data/raw/patients_raw.csv")
        validator = context.sources.pandas_default.read_dataframe(df)

        validator.expect_column_values_to_not_be_null("patient_id")

        validator.expect_column_value_lengths_to_equal(
            column="cccd",
            value=12
        )

        validator.expect_column_values_to_be_between(
            column="ket_qua_xet_nghiem",
            min_value=0,
            max_value=50
        )

        valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
        validator.expect_column_values_to_be_in_set(
            column="benh",
            value_set=valid_conditions
        )

        validator.expect_column_values_to_match_regex(
            column="email",
            regex=r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
        )

        validator.expect_column_values_to_be_unique(column="patient_id")

        validator.save_expectation_suite()
        return suite
    except Exception:
        # Fallback: trả về dict expectations thủ công
        return {
            "suite_name": "patient_data_suite",
            "expectations": [
                {"expectation": "patient_id not null"},
                {"expectation": "cccd length == 12"},
                {"expectation": "ket_qua_xet_nghiem between 0 and 50"},
                {"expectation": "benh in valid set"},
                {"expectation": "email matches regex"},
                {"expectation": "patient_id is unique"},
            ]
        }


def validate_anonymized_data(filepath: str) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # Check 1: Không còn CCCD gốc trong anonymized data
    original_df = pd.read_csv("data/raw/patients_raw.csv")
    for orig_cccd in original_df["cccd"].astype(str):
        if orig_cccd in df["cccd"].astype(str).values:
            results["success"] = False
            results["failed_checks"].append(
                f"Original CCCD {orig_cccd} still present in anonymized data"
            )

    # Check 2: Không có null values trong các cột quan trọng
    required_cols = ["patient_id", "benh", "ket_qua_xet_nghiem"]
    for col in required_cols:
        if col in df.columns and df[col].isnull().any():
            results["success"] = False
            results["failed_checks"].append(f"Null values found in column: {col}")

    # Check 3: Số rows phải bằng original
    if len(df) != len(original_df):
        results["success"] = False
        results["failed_checks"].append(
            f"Row count mismatch: anonymized={len(df)}, original={len(original_df)}"
        )

    return results
