# Dare Careers — DAX Formulas

All measures go in **Report View → Home → New Measure**.
The calculated column (Section 4) goes in **Table View → LearnerStatus table → New Column**.

---

## Data Model — Relationships (build this first)

In **Model View**, create these relationships. All are Many-to-one (*:1), single filter direction (→).
`LearnerStatus` is the central dimension table — **do not use `Learners` as the hub**.

```
LearnerStatus[Learner_ID]  →  Attendance[Learner_ID]
LearnerStatus[Learner_ID]  →  Participation[Learner_ID]
LearnerStatus[Learner_ID]  →  Assessments[Learner_ID]
DateDim[Date]              →  Attendance[Date]
```

> The `Learners` table can remain imported but leave it unrelated.
> `LearnerStatus` already contains Name, Track, Cohort, Certification_Status — use it everywhere.

---

## Section 1 — Count Measures
> Add these to the **LearnerStatus** table. Create all four before moving on.

```dax
Total Learners =
    DISTINCTCOUNT( LearnerStatus[Learner_ID] )
```

```dax
Total Graduations =
    CALCULATE(
        DISTINCTCOUNT( LearnerStatus[Learner_ID] ),
        LearnerStatus[Graduation_Status] = "Graduated"
    )
```

```dax
Total Dropouts =
    CALCULATE(
        DISTINCTCOUNT( LearnerStatus[Learner_ID] ),
        LearnerStatus[Graduation_Status] = "Dropped Out"
    )
```

```dax
Total Certifications =
    CALCULATE(
        DISTINCTCOUNT( LearnerStatus[Learner_ID] ),
        LearnerStatus[Certification_Status] = "Certified"
    )
```

---

## Section 2 — Rate Measures (Page 1 Charts)
> Depends on Section 1 measures existing first.

```dax
Graduation Rate % =
    DIVIDE( [Total Graduations], [Total Learners], 0 ) * 100
```

```dax
Certification Rate % =
    DIVIDE( [Total Certifications], [Total Learners], 0 ) * 100
```

```dax
Dropout Rate % =
    DIVIDE( [Total Dropouts], [Total Learners], 0 ) * 100
```

```dax
Attendance Rate % =
    VAR attended = CALCULATE( COUNTROWS( Attendance ), Attendance[Attended] = TRUE() )
    VAR total    = COUNTROWS( Attendance )
    RETURN DIVIDE( attended, total, 0 ) * 100
```

```dax
Avg Participation Score =
    CALCULATE(
        AVERAGE( Participation[Participation_Score] ),
        Participation[Attended_Session] = TRUE()
    )
```

```dax
Avg Assessment Score =
    AVERAGEX(
        FILTER( Assessments, Assessments[Any_Submission] = TRUE() ),
        Assessments[Assessment_Average]
    )
```

---

## Section 3 — Detailed Learner Cards (Page 2)

```dax
Count Labs Submitted =
    CALCULATE( COUNTROWS( Assessments ), Assessments[Lab_Submitted] = TRUE() )
```

```dax
Avg Labs Per Learner =
    DIVIDE( [Count Labs Submitted], DISTINCTCOUNT( Assessments[Learner_ID] ), 0 )
```

```dax
Total Class Hours =
    CALCULATE( SUM( Attendance[Duration_Hours] ), Attendance[Attended] = TRUE() )
```

```dax
Avg Hours Per Learner =
    DIVIDE( [Total Class Hours], DISTINCTCOUNT( Attendance[Learner_ID] ), 0 )
```

```dax
Avg Attendance Rate % =
    AVERAGEX(
        VALUES( LearnerStatus[Learner_ID] ),
        LearnerStatus[Attendance_Rate_Pct]
    )
```

```dax
Avg Assessment Score Per Learner =
    AVERAGEX(
        FILTER( Assessments, Assessments[Any_Submission] = TRUE() ),
        Assessments[Assessment_Average]
    )
```

---

## Section 4 — Calculated Column (LearnerStatus table)
> Table View → select LearnerStatus table → New Column (not New Measure).

```dax
Performance Tier =
    SWITCH(
        TRUE(),
        LearnerStatus[Attendance_Rate_Pct] >= 85
            && LearnerStatus[Average_Assessment_Score] >= 80,  "High Performer",
        LearnerStatus[Attendance_Rate_Pct] >= 70
            && LearnerStatus[Average_Assessment_Score] >= 65,  "On Track",
        LearnerStatus[Attendance_Rate_Pct] >= 50,              "At Risk",
        "Critical Risk"
    )
```

---


