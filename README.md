# solutii-romania-ai
# Solutii Romania (.com) — AI Civic &amp; Administrative Solutions Engine  **Solutii Romania** is an opeN SORCE
# Solutii Romania (.com) — AI Civic & Administrative Solutions Engine

**Solutii Romania** is an open-source automated intelligence pipeline powered by Python and Google Gemini AI. It monitors daily public news feeds for systemic issues, administrative bottlenecks, and negative public-sector reports in Romania, transforming each detected problem into a structured project management and administrative blueprint for civil servants.

## Generated Deliverables per Detected Issue
1. **Civil Servant Action Blueprint**: Applicable Romanian legal framework, step-by-step execution guide, and a ready-to-paste Approval Report (*Referat de Aprobare*).
2. **Stakeholder Analysis**: Identification of institutional actors, power/interest levels, and engagement strategies.
3. **Problem Tree & Objective Tree**: Root causes, systemic effects, general/specific objectives, and expected public impact.
4. **SWOT Analysis**: Internal strengths/weaknesses and external opportunities/threats.
5. **Ishikawa (Fishbone) Diagram**: Root-cause breakdown across Technology, Processes, Human Resources, and Environment/Context.
6. **Logical Framework (LogFrame)**: Objectively verifiable indicators, verification sources, and key assumptions.
7. **Activity Plan & Gantt Schedule**: Phased implementation timeline with responsible units.
8. **Estimated Budget**: Itemized financial estimation in EUR.

## Deployment Setup (100% Free via GitHub)
1. Push this repository to GitHub.
2. Go to **Settings > Secrets and variables > Actions** and add a new repository secret named `GEMINI_API_KEY` with your Google AI Studio API key.
3. Go to **Settings > Pages**, set **Source** to `Deploy from a branch`, select `main` branch and `/docs` folder, and click **Save**.
4. Go to **Actions > Daily AI Civic Monitor & Site Builder** and click **Run workflow** to trigger the first live scan.

5. MIT License

Copyright (c) 2026 Solutii Romania Open-Source Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
