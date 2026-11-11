# Research Log – RainWatch Rwanda

**Student:** Shema Can Daddy Nathan · **ID:** 20251SEN067
**Course:** INSY 8311 Database Development with PL/SQL · **Instructor:** Eric Maniraguha
**Project:** RainWatch Rwanda: Rainfall Risk Monitoring and Flood Early-Warning System (Oracle PL/SQL)
**GitHub:** https://github.com/can-daddy/nathan_20251SEN067_rainWatch

## 1. Sources

| # | Source (APA) | Type | Link | Key finding | Gap it shows |
|---|--------------|------|------|-------------|--------------|
| 1 | Nakulopa, F., Vanderkelen, I., Van de Walle, J., Van Lipzig, N. P. M., Tabari, H., Jacobs, L., Tweheyo, C., Dewitte, O., & Thiery, W. (2022). Evaluation of high-resolution precipitation products over the Rwenzori Mountains (Uganda). *Journal of Hydrometeorology, 23*. | Research paper | https://doi.org/10.1175/JHM-D-21-0106.1 | Satellite and reanalysis rainfall were compared with rain gauges in a mountain region of East Africa. ERA5 showed a persistent wet bias and underestimated how often intense rain occurs. | Gridded rainfall can differ from local measurements, so RainWatch keeps its thresholds editable and presents results as risk screening. |
| 2 | Gleixner, S., Demissie, T., & Diro, G. T. (2020). Did ERA5 improve temperature and precipitation reanalysis over East Africa? *Atmosphere, 11*(9), 996. | Research paper | https://doi.org/10.3390/atmos11090996 | Assesses whether ERA5 improved on earlier reanalysis over East Africa. Performance differs by region, so local checking is needed. | ERA5 must be checked locally. RainWatch stores a `DATA_SOURCE` for each reading so other sources can be added. |
| 3 | Bagiliko, J., Stern, D., Ndanguza, D., & Torgbor, F. F. (2025). *Validation of satellite and reanalysis rainfall products against rain gauge observations in Ghana and Zambia* (arXiv:2501.14829). | Research paper (preprint) | https://arxiv.org/abs/2501.14829 | Eight products were compared with rain gauges. All had very low skill for heavy and violent rain, although they often flagged those days as rainy and underestimated the amount. Area averages are compared with point gauges. | Heavy rain is the key case for flood warning. RainWatch ranks each day against the district's own history and reports this limit openly. |
| 4 | International Federation of Red Cross and Red Crescent Societies. (n.d.). *Rwanda: Floods and landslides – DREF final report (MDRRW022)*. ReliefWeb. | Report | https://reliefweb.int/report/rwanda/rwanda-floods-and-landslides-dref-final-report-mdrrw022 | Rainfall of 110–130 mm was reported on 3 May 2023, far above earlier flood events (35.6–60.88 mm). Six Western districts were strongly affected: Rubavu, Nyabihu, Ngororero, Karongi, Rutsiro and Nyamasheke. | Provides a real past event for the back-test and the districts to include. |
| 5 | The EastAfrican. (2023). *Rwanda's devastating floods, landslides deaths rise to 130*. | Statistic (news report citing ministry data) | https://theeastafrican.co.ke/tea/news/east-africa/rwanda-floods-death-toll-rises-4222646 | Floods and landslides have cost Rwanda over 600 lives since 2018, with about 30,600 houses destroyed. | Shows the size of the problem. The figures exist, but not a district-level record linking rain, alert and response. |
| 6 | Global Facility for Disaster Reduction and Recovery. (n.d.). *Rwanda: Building resilience to flood hazards in Northwest Rwanda through improved national and local capacity*. | Existing system | https://www.gfdrr.org/en/rwanda-building-resilience-flood-hazards-northwest-rwanda-through-improved-national-and-local | A flood early-warning system was built for the Sebeya River Basin, linked to a national platform, with warnings sent through a smartphone app. | It focuses on forecasting and sending warnings for one basin. It does not describe a register of how each alert was handled, which RainWatch adds. |
| 7 | Open-Meteo. (n.d.). *Historical weather API*. | Dataset | https://open-meteo.com/en/docs/historical-weather-api | Free daily precipitation for any coordinates since 1940, licence CC BY 4.0, free for non-commercial use, no personal data. | The data is modelled, not measured. It gives the rain series; alerts and responses are created by the PL/SQL system. |
| 8 | Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A., Muñoz-Sabater, J., … Thépaut, J.-N. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society, 146*(730), 1999–2049. | Research paper (origin of the data) | https://doi.org/10.1002/qj.3803 | Describes ERA5, the ECMWF reanalysis behind the Open-Meteo data. | Explains what the data is and why its grid resolution limits local accuracy. |
| 9 | Oracle. (2025). *Oracle Database PL/SQL packages and types reference, 19c*. | Technical source | https://docs.oracle.com/en/database/oracle/oracle-database/19/arpls/ | `DBMS_SCHEDULER` creates jobs that run PL/SQL on a schedule, for example every day. | Confirms the tool for the daily alert job (innovation). |

## 2. Dataset summary

| Item | Detail |
|---|---|
| Dataset | Open-Meteo Historical Weather API, daily `precipitation_sum` |
| Coverage | 10–15 Rwandan districts, about 10 years of daily records (over 30,000 rows) |
| Licence | CC BY 4.0 (credit: "Weather data by Open-Meteo.com") |
| Personal data | None |
| First test | Rubavu, 3 May 2023: 26.0 mm, 95.3rd percentile of 2014–2023 daily rain (P95 = 25.5 mm, P99 = 38.1 mm) |

## 3. Gaps found

1. Existing work focuses on **forecasting and sending warnings**.
2. The sources reviewed do not describe a **district-level record** that links rainfall → risk level → alert → action → closing.
3. Gridded rainfall has **known accuracy limits**, especially for heavy rain. Thresholds must be **editable** and every change **audited**.

## 4. How the research shaped the project

- **Source 1, 2, 3:** thresholds come from each district's own rainfall history (percentiles), are editable, and RainWatch is described as risk screening.
- **Source 4:** the six affected districts and the 2–3 May 2023 event are used for the back-test.
- **Source 6:** RainWatch adds the missing alert-handling record (status, action, audit log).
- **Source 9:** a daily `DBMS_SCHEDULER` job creates alerts automatically.
