import pandas as pd

# reading in the csv as a pandas dataframe, only using relevant columns needed for output file
df = pd.read_csv('HospitalGeneralInformation.csv', usecols=["County Name", "State", "Hospital Type",
                                                            "Hospital overall rating"])

# dropping any rows with a missing value
df.dropna(how="any")

# creating an output dataframe
output = pd.DataFrame()

# combining the County Name and State columns to form county_state for output
df["county_state"] = df["County Name"] + ", " + df["State"]
output["county_state"] = df["county_state"].drop_duplicates()

# counting number of hospitals, grouped by county and state
output["num_hospitals"] = df.groupby(["county_state"])["Hospital Type"].transform("count")

# counting only acute care hospitals
df["Hospital Type"] = df["Hospital Type"].mask(df["Hospital Type"].ne('Acute Care Hospitals'))
output["num_acute_care_hospitals"] = df.groupby(["county_state"])["Hospital Type"].transform("count")

# computing percentage of hospitals that are acute care hospitals by
# 100 * number acute / number hospitals rounded to 2 decimal points
output["pct_acute_care"] = (100 * output["num_acute_care_hospitals"] / output["num_hospitals"]).round(2)

# removing the rows without available rating data
df = df[df["Hospital overall rating"] != "Not Available"]

# converting Hospital overall rating column to numeric so average can be computed
df["Hospital overall rating"] = pd.to_numeric(df["Hospital overall rating"])

# sorting by number of hospitals decreasing
output.sort_values("num_hospitals", ascending=False, inplace=True)

# computing average rating rounded to hundredths using join
output = output.set_index("county_state").join(df.groupby("county_state", as_index=False)["Hospital overall rating"]
                                               .mean().round(2).set_index("county_state"))
# renames column created by join
output = output.rename(columns={"Hospital overall rating": "avg_acute_care_rating"})

# computing median using a join
output = output.join(df.groupby("county_state", as_index=False)["Hospital overall rating"]
                                               .median().set_index("county_state"))
# renames column created by join
output = output.rename(columns={"Hospital overall rating": "median_acute_care_rating"})

# creates output csv with correct name
output.to_csv("hospitals_by_county.csv")
