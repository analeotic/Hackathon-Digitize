"""
Confidence Scoring System for Field-Level Quality Assessment
Provides confidence scores (0-1) for each extracted field
"""
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime


class ConfidenceScorer:
    """Calculate confidence scores for extracted data fields"""

    def __init__(self):
        """Initialize confidence scorer with validation rules"""
        # Thai name patterns (common titles and characters)
        self.thai_titles = ["นาย", "นาง", "นางสาว", "ด.ช.", "ด.ญ.", "พ.ต.ท.", "พ.ต.อ.", "พ.อ.", "ร.ต."]
        self.thai_char_pattern = re.compile(r'^[ก-๏\s\.]+$')

        # Thai provinces for validation
        self.thai_provinces = [
            "กรุงเทพมหานคร", "กระบี่", "กาญจนบุรี", "กาฬสินธุ์", "กำแพงเพชร",
            "ขอนแก่น", "จันทบุรี", "ฉะเชิงเทรา", "ชลบุรี", "ชัยนาท",
            "เชียงราย", "เชียงใหม่", "ตรัง", "ตราด", "นครนายก",
            "นครปฐม", "นครพนม", "นครราชสีมา", "นครศรีธรรมราช", "นครสวรรค์",
            # ... (abbreviated for brevity)
        ]

    def score_extracted_data(self, data: Dict) -> Dict:
        """
        Add confidence scores to all fields in extracted data

        Args:
            data: Extracted data dictionary

        Returns:
            Data with added confidence scores and metadata
        """
        result = {
            "data": data,
            "confidence_scores": {},
            "validation_warnings": [],
            "low_confidence_fields": [],
            "overall_confidence": 0.0,
            "field_count": {
                "total": 0,
                "high_confidence": 0,  # >= 0.9
                "medium_confidence": 0,  # 0.7-0.9
                "low_confidence": 0  # < 0.7
            }
        }

        # Score submitter
        if "submitter" in data and data["submitter"]:
            submitter_scores = self._score_person(data["submitter"], "submitter")
            result["confidence_scores"]["submitter"] = submitter_scores
            self._update_stats(result, submitter_scores)

        # Score spouse
        if "spouse" in data and data["spouse"]:
            spouse_scores = self._score_person(data["spouse"], "spouse")
            result["confidence_scores"]["spouse"] = spouse_scores
            self._update_stats(result, spouse_scores)

        # Score relatives
        if "relatives" in data and data["relatives"]:
            relatives_scores = []
            for i, relative in enumerate(data["relatives"]):
                rel_score = self._score_person(relative, f"relative_{i}")
                relatives_scores.append(rel_score)
                self._update_stats(result, rel_score)
            result["confidence_scores"]["relatives"] = relatives_scores

        # Score positions
        if "submitter_positions" in data and data["submitter_positions"]:
            pos_scores = []
            for i, pos in enumerate(data["submitter_positions"]):
                p_score = self._score_position(pos, f"position_{i}")
                pos_scores.append(p_score)
                self._update_stats(result, p_score)
            result["confidence_scores"]["submitter_positions"] = pos_scores

        # Score assets
        if "assets" in data and data["assets"]:
            asset_scores = []
            for i, asset in enumerate(data["assets"]):
                a_score = self._score_asset(asset, f"asset_{i}")
                asset_scores.append(a_score)
                self._update_stats(result, a_score)
            result["confidence_scores"]["assets"] = asset_scores

        # Score statements
        if "statements" in data and data["statements"]:
            stmt_scores = []
            for i, stmt in enumerate(data["statements"]):
                s_score = self._score_statement(stmt, f"statement_{i}")
                stmt_scores.append(s_score)
                self._update_stats(result, s_score)
            result["confidence_scores"]["statements"] = stmt_scores

        # Calculate overall confidence
        if result["field_count"]["total"] > 0:
            result["overall_confidence"] = (
                result["field_count"]["high_confidence"] * 1.0 +
                result["field_count"]["medium_confidence"] * 0.8 +
                result["field_count"]["low_confidence"] * 0.5
            ) / result["field_count"]["total"]

        return result

    def _score_person(self, person: Dict, prefix: str) -> Dict:
        """Score person-related fields (submitter/spouse/relative)"""
        scores = {}

        # Score title
        if "title" in person:
            title = person.get("title", "")
            if title in self.thai_titles:
                scores["title"] = 0.95
            elif title and self.thai_char_pattern.match(title):
                scores["title"] = 0.75
            elif title:
                scores["title"] = 0.50
            else:
                scores["title"] = 0.0

        # Score first name
        if "first_name" in person:
            fname = person.get("first_name", "")
            scores["first_name"] = self._score_thai_text(fname, min_len=2, max_len=30)

        # Score last name
        if "last_name" in person:
            lname = person.get("last_name", "")
            scores["last_name"] = self._score_thai_text(lname, min_len=2, max_len=30)

        # Score age
        if "age" in person:
            age = person.get("age")
            if age is not None:
                if 18 <= age <= 100:
                    scores["age"] = 0.95
                elif 0 <= age <= 120:
                    scores["age"] = 0.70
                else:
                    scores["age"] = 0.20  # Suspicious age
            else:
                scores["age"] = 0.0

        return scores

    def _score_position(self, position: Dict, prefix: str) -> Dict:
        """Score position-related fields"""
        scores = {}

        # Score position name
        if "position_name" in position:
            pos_name = position.get("position_name", "")
            scores["position_name"] = self._score_thai_text(pos_name, min_len=3, max_len=100)

        # Score dates (start/end)
        for date_field in ["position_start", "position_ending"]:
            year = position.get(f"{date_field}_year", "")
            month = position.get(f"{date_field}_month", "")
            day = position.get(f"{date_field}_date", "")

            scores[date_field] = self._score_date(year, month, day)

        return scores

    def _score_asset(self, asset: Dict, prefix: str) -> Dict:
        """Score asset-related fields"""
        scores = {}

        # Score asset name
        if "asset_name" in asset:
            name = asset.get("asset_name", "")
            scores["asset_name"] = self._score_thai_text(name, min_len=2, max_len=200)

        # Score asset type
        if "asset_type_id" in asset:
            type_id = asset.get("asset_type_id")
            if type_id is not None and 1 <= type_id <= 33:
                scores["asset_type_id"] = 0.95
            elif type_id is not None:
                scores["asset_type_id"] = 0.40  # Invalid type
            else:
                scores["asset_type_id"] = 0.0

        # Score valuation
        if "valuation" in asset:
            val = asset.get("valuation")
            if val is not None:
                if 0 <= val <= 1_000_000_000:  # 0 to 1 billion baht
                    scores["valuation"] = 0.95
                elif val > 1_000_000_000:
                    scores["valuation"] = 0.70  # Very high value (suspicious but possible)
                else:
                    scores["valuation"] = 0.20  # Negative value
            else:
                scores["valuation"] = 0.0

        # Score acquiring date
        year = asset.get("acquiring_year", "")
        month = asset.get("acquiring_month", "")
        day = asset.get("acquiring_date", "")
        scores["acquiring_date"] = self._score_date(year, month, day)

        # Score ownership flags
        owner_sub = asset.get("owner_by_submitter", False)
        owner_spouse = asset.get("owner_by_spouse", False)
        owner_child = asset.get("owner_by_child", False)

        # At least one owner should be true
        if owner_sub or owner_spouse or owner_child:
            scores["ownership"] = 0.95
        else:
            scores["ownership"] = 0.50  # No owner specified (warning)

        return scores

    def _score_statement(self, statement: Dict, prefix: str) -> Dict:
        """Score statement-related fields"""
        scores = {}

        # Score statement name
        if "statement_name" in statement:
            name = statement.get("statement_name", "")
            scores["statement_name"] = self._score_thai_text(name, min_len=2, max_len=200)

        # Score statement type
        if "statement_type_id" in statement:
            type_id = statement.get("statement_type_id")
            if type_id is not None and 1 <= type_id <= 4:
                scores["statement_type_id"] = 0.95
            elif type_id is not None:
                scores["statement_type_id"] = 0.40
            else:
                scores["statement_type_id"] = 0.0

        # Score valuation
        if "valuation" in statement:
            val = statement.get("valuation")
            if val is not None and val >= 0:
                scores["valuation"] = 0.90
            elif val is not None:
                scores["valuation"] = 0.20
            else:
                scores["valuation"] = 0.0

        return scores

    def _score_thai_text(self, text: str, min_len: int = 1, max_len: int = 100) -> float:
        """
        Score Thai text field based on:
        - Contains Thai characters
        - Reasonable length
        - No suspicious patterns
        """
        if not text or text.strip() == "":
            return 0.0

        text = text.strip()

        # Check length
        if len(text) < min_len:
            return 0.30  # Too short
        if len(text) > max_len:
            return 0.60  # Suspiciously long

        # Check if mostly Thai characters
        if self.thai_char_pattern.match(text):
            return 0.95  # High confidence (valid Thai text)

        # Contains some Thai characters
        thai_chars = len([c for c in text if '\u0E00' <= c <= '\u0E7F'])
        if thai_chars > len(text) * 0.5:
            return 0.80  # Medium-high confidence

        # Mostly non-Thai (might be English/numbers)
        if thai_chars > 0:
            return 0.65  # Medium confidence

        return 0.40  # Low confidence (no Thai characters)

    def _score_date(self, year: str, month: str, day: str) -> float:
        """
        Score date fields based on:
        - Valid year range (1900-2100 Christian, 2443-2643 Buddhist)
        - Valid month (1-12)
        - Valid day (1-31)
        """
        try:
            if not year or not month or not day:
                return 0.0  # Missing date components

            y = int(year) if year else 0
            m = int(month) if month else 0
            d = int(day) if day else 0

            # Convert Buddhist year to Christian if needed
            if y > 2400:
                y = y - 543

            # Check valid ranges
            if not (1900 <= y <= 2100):
                return 0.20  # Invalid year
            if not (1 <= m <= 12):
                return 0.30  # Invalid month
            if not (1 <= d <= 31):
                return 0.30  # Invalid day

            # Try to create actual date (validates day in month)
            try:
                datetime(y, m, d)
                return 0.95  # Valid date
            except ValueError:
                return 0.60  # Invalid day for month (e.g., Feb 30)

        except (ValueError, TypeError):
            return 0.10  # Parse error

    def _update_stats(self, result: Dict, field_scores: Dict):
        """Update field count statistics"""
        for field, score in field_scores.items():
            result["field_count"]["total"] += 1

            if score >= 0.9:
                result["field_count"]["high_confidence"] += 1
            elif score >= 0.7:
                result["field_count"]["medium_confidence"] += 1
            else:
                result["field_count"]["low_confidence"] += 1

                # Track low confidence fields
                result["low_confidence_fields"].append({
                    "field": field,
                    "confidence": score
                })

                # Add warning
                if score < 0.5:
                    result["validation_warnings"].append(
                        f"Low confidence ({score:.0%}): {field}"
                    )

    def generate_confidence_report(self, scored_data: Dict) -> str:
        """Generate human-readable confidence report"""
        report = []
        report.append("=" * 60)
        report.append("CONFIDENCE SCORE REPORT")
        report.append("=" * 60)

        # Overall stats
        fc = scored_data["field_count"]
        report.append(f"\nOverall Confidence: {scored_data['overall_confidence']:.1%}")
        report.append(f"\nField Statistics:")
        report.append(f"  Total Fields: {fc['total']}")
        report.append(f"  ✅ High (≥90%):   {fc['high_confidence']} ({fc['high_confidence']/fc['total']*100:.0f}%)")
        report.append(f"  ⚠️  Medium (70-90%): {fc['medium_confidence']} ({fc['medium_confidence']/fc['total']*100:.0f}%)")
        report.append(f"  ❌ Low (<70%):    {fc['low_confidence']} ({fc['low_confidence']/fc['total']*100:.0f}%)")

        # Low confidence fields
        if scored_data["low_confidence_fields"]:
            report.append(f"\n⚠️  Low Confidence Fields ({len(scored_data['low_confidence_fields'])}):")
            for field_info in scored_data["low_confidence_fields"][:10]:  # Top 10
                report.append(f"  - {field_info['field']}: {field_info['confidence']:.0%}")

        # Validation warnings
        if scored_data["validation_warnings"]:
            report.append(f"\n❗ Validation Warnings ({len(scored_data['validation_warnings'])}):")
            for warning in scored_data["validation_warnings"][:10]:  # Top 10
                report.append(f"  - {warning}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)


def add_confidence_scores(extracted_data: Dict) -> Dict:
    """
    Convenience function to add confidence scores to extracted data

    Args:
        extracted_data: Raw extracted data

    Returns:
        Data with confidence scores and validation warnings
    """
    scorer = ConfidenceScorer()
    return scorer.score_extracted_data(extracted_data)
