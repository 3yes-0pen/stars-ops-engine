import pandas as pd

s = pd.read_parquet("data/interim/summary_2027.parquet")
c = pd.read_parquet("data/interim/cai_2027.parquet")
d = s.merge(c[["contract_id", "puerto_rico_only", "fac_overall", "fac_overall_message"]],
            on="contract_id", how="left")

num = d[d["overall"].notna()].copy()
dis = ["disaster_2024_pct", "disaster_2025_pct"]

print("contracts in file:", len(d))
print("numeric Overall:", len(num))
print("\nOrganization types among numeric Overall:")
print(num["organization_type"].value_counts().to_string())
print("\nDisaster columns (all contracts); look at min and max:")
print(d[dis].describe().loc[["count", "min", "max"]].to_string())

num["flagged"] = num[dis].max(axis=1) >= 25
num["pr_only"] = num["puerto_rico_only"].astype(str).str.strip().str.lower().eq("yes")
print("\nAmong numeric Overall:")
print("  disaster-flagged (>= 25 on either column):", int(num["flagged"].sum()))
print("  Puerto Rico-only:", int(num["pr_only"].sum()))
print("  flagged or PR-only:", int((num["flagged"] | num["pr_only"]).sum()))
print("  headline population (neither):", int((~(num["flagged"] | num["pr_only"])).sum()))
print("\nCAI category (FAC) among numeric Overall:")
print(num["fac_overall"].value_counts(dropna=False).to_string())
print("contracts with numeric Overall but no numeric FAC:", int(num["fac_overall"].isna().sum()))