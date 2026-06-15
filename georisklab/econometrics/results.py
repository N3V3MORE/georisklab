from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RegressionResult:
    coefficients: pd.DataFrame
    metadata: dict
    nobs: int
    adjusted_r2: float
    se_type: str

    def to_frame(self) -> pd.DataFrame:
        df = self.coefficients.copy()
        df["nobs"] = self.nobs
        df["adjusted_r2"] = self.adjusted_r2
        df["se_type"] = self.se_type
        return df
