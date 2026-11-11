# RainWatch Rwanda
### Rainfall Risk Monitoring and Flood Early-Warning System (Oracle PL/SQL)

| | |
|---|---|
| **Student** | Shema Can Daddy Nathan |
| **Student ID** | 20251SEN067 |
| **Course** | INSY 8311 – Database Development with PL/SQL (Final Exam, Capstone Project) |
| **Instructor** | Eric Maniraguha |
| **University** | Adventist University of Central Africa (AUCA) |
| **Current phase** | Phase 0 – Research, Data Source and Proposal |

---

## 1. Problem statement

Heavy rain causes floods and landslides in Rwanda again and again. Data from the Ministry in charge of Emergency Management shows that floods and landslides have cost over 600 lives since 2018. On 2–3 May 2023, rainfall of 110–130 mm was reported, far above the 35.6–60.9 mm recorded in earlier flood events, and six districts in the Western Province were badly hit.

Forecasting and early-warning projects already exist. But the public sources I found describe forecasting and sending warnings. They do not describe a district-level record that links **rainfall → risk level → alert → action taken → closing**. Without such a record, it is hard to answer simple questions: *Which warnings were acted on? How long did the response take? Which alerts were ignored?*

## 2. Purpose and users

**RainWatch Rwanda** is a smoke alarm plus a logbook:
- the **smoke alarm** checks the daily rain numbers and raises a risk alert;
- the **logbook** records who was told, what they did, and when the alert was closed.

| User | What they do in the system |
|---|---|
| District disaster officer | Sees today's risk by district and accepts alerts |
| Sector officer (role) | Records the action taken (for example: "warned families near the river") |
| Manager / auditor | Reads reports: response time, ignored alerts, history |

**What it is not:** it is not a weather forecast and it does not replace Meteo Rwanda. It is a database-driven **decision-support and tracking system**.

## 3. Objectives

**Main objective:** To build an Oracle PL/SQL system that turns daily rainfall data into risk alerts and tracks how each alert is handled.

**Specific objectives**
1. Store daily rainfall for selected Rwandan districts in a normalized (3NF) Oracle database.
2. Calculate risk levels with PL/SQL functions, using thresholds taken from each district's own rainfall history.
3. Create alerts automatically with a scheduled job, and manage the full alert life cycle with procedures and triggers.
4. Keep an audit log of every change and give officers a simple Streamlit app to view and update alerts.
5. Test the system on a past flood event (2–3 May 2023) and report how the event days rank in each district's own rainfall history.

## 4. Data source

| Item | Detail |
|---|---|
| Data | Daily precipitation (`precipitation_sum`) for 10–15 Rwandan districts, about 10 years of daily records |
| Provider | Open-Meteo Historical Weather API (https://open-meteo.com/en/docs/historical-weather-api) |
| Origin | ECMWF ERA5 reanalysis (Hersbach et al., 2020) |
| Licence | Free for non-commercial use; data under CC BY 4.0. Attribution: **"Weather data by Open-Meteo.com"** |
| Size | More than 30,000 rows (districts × days) |
| Personal data | None |

**Districts chosen (planned):** Rubavu, Nyabihu, Ngororero, Karongi, Rutsiro, Nyamasheke (Western Province, hit in May 2023), plus Musanze, Gakenke, Burera, and Kigali districts (Gasabo, Kicukiro, Nyarugenge).

**Honest note about data quality:** ERA5 is a *model estimate*, not a rain-gauge reading. Studies in East Africa report a wet bias over complex terrain (Nakulopa et al., 2022) and weak skill on extreme rain (Bagiliko et al., 2025). For this reason RainWatch is a **risk-screening tool**, thresholds are stored in a table so they can be edited, and every reading keeps a `DATA_SOURCE` column so another source (such as CHIRPS) can be added later.

**First test result:** for Rubavu, the data gave 12.3 mm (1 May), 11.0 mm (2 May) and 26.0 mm (3 May 2023), much lower than the 110–130 mm reported by the national meteorological agency on 3 May. This is expected: ERA5 averages rain over a grid cell about 25–31 km wide, while the reported value is from a point, and gridded products tend to underestimate the intensity of heavy rain (Bagiliko et al., 2025; Nakulopa et al., 2022). So RainWatch does **not** depend on absolute millimetres. It ranks each day against the district's own history from the same data source.

**Ranking test (Rubavu, history 2014–2023):** the 95th percentile of daily rain is 25.5 mm and the 99th is 38.1 mm. The 26.0 mm of 3 May 2023 ranks at the 95.3rd percentile (3-day total 49.3 mm, 88.4th percentile). With the planned rule, RainWatch would raise a MEDIUM alert on that day, not HIGH. This is reported honestly: gridded data smooths heavy storms. The other five Western districts will be tested the same way.


## 5. Innovation

- **Option:** Smart automation (scheduler and alerts)
- **Tools:** Oracle `DBMS_SCHEDULER` (nightly job) + a **Streamlit** app in Python (`python-oracledb`) connected to the real Oracle database
- **How it works:** a small Python script loads new daily rainfall into a staging table. The Oracle job runs every day, checks the new readings and creates alerts. Officers use the Streamlit app to accept alerts, record actions and close them.
- **Rule:** business rules stay in PL/SQL. Streamlit only shows and sends data; procedures and triggers enforce the rules.

## 6. Planned tables (3NF)

| Table | Purpose |
|---|---|
| `DISTRICT` | Districts and provinces, with centre coordinates |
| `RAIN_READING` | One row per district per day (rain in mm, `DATA_SOURCE`) |
| `RISK_LEVEL` | Lookup: LOW, MEDIUM, HIGH |
| `THRESHOLD_RULE` | Editable rain limits per district (1-day and 3-day totals) |
| `OFFICER` | Officer roles and the district they cover (role accounts, no real personal data) |
| `ALERT` | Alerts with status: NEW → ACKNOWLEDGED → ACTION_TAKEN → CLOSED |
| `ALERT_ACTION` | Actions recorded for each alert |
| `AUDIT_LOG` | Who changed what and when |
| `STG_RAIN` | Staging table for the Python loader |

## 7. Planned PL/SQL features

| Feature | Where it is used |
|---|---|
| Function `fn_risk_level` | Returns LOW / MEDIUM / HIGH from 1-day and 3-day rain totals |
| Procedure `sp_compute_thresholds` | Calculates the 95th and 99th percentile of each district's history (`PERCENTILE_CONT`) and saves them as starting limits |
| Procedure `sp_generate_alerts` | Uses a cursor over new readings and creates an alert only if no open alert exists |
| Procedures `sp_acknowledge_alert`, `sp_record_action`, `sp_close_alert` | Move an alert through its life cycle |
| Cursor report | Alerts by district and month, average response time, alerts never acknowledged |
| Trigger on `RAIN_READING` | Blocks negative or impossible rainfall and future dates |
| Trigger on `ALERT` | Allows only valid status changes (for example, NEW cannot jump to CLOSED) |
| Trigger on `ALERT` | Blocks closing an alert that has no recorded action |
| Restriction rule | Blocks changes to `THRESHOLD_RULE` on weekends and public holidays |
| Audit triggers | Write every insert, update and delete into `AUDIT_LOG` |
| Package `pkg_rainwatch` | Groups the functions and procedures |
| Custom exceptions | `e_invalid_transition`, `e_no_action_recorded` |
| Scheduler job `JOB_DAILY_RAINWATCH` | Runs `sp_generate_alerts` every day |

## 8. How the system works

1. **Python loader** downloads yesterday's rain from Open-Meteo and writes it to `STG_RAIN`.
2. **Oracle job** validates the rows, moves them into `RAIN_READING`, and calls `sp_generate_alerts`.
3. **PL/SQL** calculates the risk level and creates alerts.
4. **Streamlit app** shows open alerts; an officer accepts, records an action and closes the alert.
5. **Triggers** enforce the rules and write the audit log.

## 9. Expected results

- A working Oracle database with real rainfall data loaded and validated.
- Alerts created automatically by the nightly job.
- A live Streamlit demonstration of the full alert life cycle.
- A back-test on 2–3 May 2023 for the six Western districts, reporting whether the event days rank in the top percentiles of each district's history and whether alerts appear on or before the event. The result will be reported honestly, even if some districts show no alert.
- Reports: response time, ignored alerts and history by district.

## 10. Limitations

- Rainfall is modelled data, not gauge data, and is weakest for extreme rain.
- Alerts and officer actions are created by the system and by demonstration users, because no public dataset of real responses exists.
- The system supports officers; it is not an official flood forecast.
- Future work: correct the bias with local gauge data, or add blended products such as CHIRPS or ENACTS-Rwanda (Siebert et al., 2019), if access is available.

## 11. Project phases

| Phase | Focus | Status |
|---|---|---|
| 0 | Research, data source, proposal | In progress |
| I | Business process modeling (BPMN/UML) | Planned |
| II | Data sourcing and normalization (3NF, ERD, dictionary) | Planned |
| III | Pluggable database (PDB) creation | Planned |
| IV | Tables and data loading | Planned |
| V | PL/SQL development | Planned |
| VI | Triggers, restriction rule, audit | Planned |
| VII | Documentation, innovation demo, final presentation | Planned |

## 12. Repository structure

```
/
├── README.md
├── docs/
│   ├── research/research_log.md
│   ├── proposal/RainWatch_Proposal.docx
│   └── presentation/RainWatch_Phase0.pptx
├── data/
├── innovation/        (added in later phases)
└── sql/               (added in later phases)
```

## 13. References (APA)

Bagiliko, J., Stern, D., Ndanguza, D., & Torgbor, F. F. (2025). *Validation of satellite and reanalysis rainfall products against rain gauge observations in Ghana and Zambia* (arXiv:2501.14829). https://arxiv.org/abs/2501.14829

Gleixner, S., Demissie, T., & Diro, G. T. (2020). Did ERA5 improve temperature and precipitation reanalysis over East Africa? *Atmosphere, 11*(9), 996. https://doi.org/10.3390/atmos11090996

Global Facility for Disaster Reduction and Recovery. (n.d.). *Rwanda: Building resilience to flood hazards in Northwest Rwanda through improved national and local capacity*. https://www.gfdrr.org/en/rwanda-building-resilience-flood-hazards-northwest-rwanda-through-improved-national-and-local

Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., … Thépaut, J.-N. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society, 146*(730), 1999–2049. https://doi.org/10.1002/qj.3803

International Federation of Red Cross and Red Crescent Societies. (n.d.). *Rwanda: Floods and landslides – DREF final report (MDRRW022)*. ReliefWeb. https://reliefweb.int/report/rwanda/rwanda-floods-and-landslides-dref-final-report-mdrrw022

Nakulopa, F., Vanderkelen, I., Van de Walle, J., Van Lipzig, N. P. M., Tabari, H., Jacobs, L., Tweheyo, C., Dewitte, O., & Thiery, W. (2022). Evaluation of high-resolution precipitation products over the Rwenzori Mountains (Uganda). *Journal of Hydrometeorology, 23*. https://doi.org/10.1175/JHM-D-21-0106.1

Open-Meteo. (n.d.). *Historical weather API*. https://open-meteo.com/en/docs/historical-weather-api

Oracle. (2025). *Oracle Database PL/SQL packages and types reference, 19c*. https://docs.oracle.com/en/database/oracle/oracle-database/19/arpls/

The EastAfrican. (2023). *Rwanda's devastating floods, landslides deaths rise to 130*. https://theeastafrican.co.ke/tea/news/east-africa/rwanda-floods-death-toll-rises-4222646

---
*Weather data by Open-Meteo.com (CC BY 4.0).*
