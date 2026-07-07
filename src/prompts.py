INSPECTION_EXTRACTION_PROMPT = """
You are an AI system that extracts structured information from a building inspection report.

Return ONLY valid JSON.

Extract every area mentioned.
Do not assume room names.
Return exactly what is present in the report.

Return this structure:

{
    "property": {
        "customer_name": "",
        "address": "",
        "property_type": ""
    },
    "observations": [
        {
            "area": "",
            "issue": "",
            "description": "",
            "severity_hint": "",
            "page": "",
            "image_reference": ""
        }
    ]
}

Inspection Report:

<<DOCUMENT>>
"""
THERMAL_EXTRACTION_PROMPT = """
You are an AI system that extracts structured information from a thermal inspection report.

Rules:

1. Never invent values.
2. Return ONLY valid JSON.
3. Preserve page numbers.
4. Extract hotspot temperature.
5. Extract coldspot temperature.
6. Extract observations.
7. If missing write "Not Available".

Extract every area mentioned.
Do not assume room names.
Return exactly what is present in the report.

Return JSON:

{
    "thermal_observations":[
        {
            "area":"",
            "page":"",
            "hotspot":"",
            "coldspot":"",
            "observation":""
        }
    ]
}

Thermal Report:

<<DOCUMENT>>
"""
DDR_JSON_PROMPT = """
You are a Senior Building Diagnostic Engineer.

Using ONLY the validated JSON below, create a structured Detailed Diagnostic Report.

Rules:

1. Never invent facts.
2. If information is unavailable, write "Not Available".
3. If conflicts exist, include them.
4. Use simple client-friendly language.
5. Return ONLY valid JSON.

Return a report with these sections:
1. Property Issue Summary
2. Area-wise Observations
3. Probable Root Cause
4. Severity Assessment
5. Recommended Actions
6. Additional Notes
7. Missing / Unclear Information

Return exactly this structure:

{
  "property_issue_summary": "...",

  "areas": [
    {
      "area": "...",
      "observations": "...",
      "root_cause": "...",
      "severity": "...",
      "severity_reason": "...",
      "recommended_actions": "...",
      "additional_notes": "...",
      "missing_information": "...",
      "images": []
    }
  ],

  "overall_notes": "...",

  "overall_missing_information": "..."
}

Validated Data:

{data}
"""