# API Lab: Testing QuickPizza with pytest and requests

This repository contains automated API tests for the QuickPizza API (`https://quickpizza.grafana.com`) as part of ITCS386 (Software Verification and Validation).

---

## 1. Setup and Installation

### Prerequisites
- Python 3.10 or newer
- `curl`
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd api-lab
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Running Tests

Run the full pytest suite with verbose output:
```bash
pytest -v
```

Generate the self-contained HTML test report:
```bash
pytest -v --html=report.html --self-contained-html
```

---

## 3. Input Domain Modeling (Part A: Ratings)

For `POST /api/ratings`, the request requires `pizza_id`, `stars`, and an `Authorization` header with a valid user token.

### Input Domain Model Table & Base Choice Coverage

| Characteristic | Blocks | Values in the tests | Test covering the block |
| :--- | :--- | :--- | :--- |
| **C1 Value of stars** | below 1 | `0` | `test_stars_out_of_range[0]` |
| | 1 to 5 (base) | `3` | `test_base_choice_is_saved` |
| | above 5 | `6` | `test_stars_out_of_range[6]` |
| **C2 Type of stars** | whole number (base) | `3` | `test_base_choice_is_saved` |
| | decimal | `3.5` | `test_stars_decimal_type_is_refused` |
| | text | `"3"` | `test_stars_text_type_is_refused` |
| | missing | no field | `test_stars_missing_is_refused` |
| **C3 Pizza** | exists (base) | a new pizza | `test_base_choice_is_saved` |
| | does not exist | `999999999` | `test_pizza_does_not_exist_is_refused` |
| **C4 Token** | the user's own (base) | from `auth` | `test_base_choice_is_saved` |
| | none | no header | `test_token_missing_is_refused` |
| | wrong length | `token short` | `test_token_wrong_length_is_refused` |

### Base Choice Coverage Summary
- **Base Choice Test:** `test_base_choice_is_saved` tests the base combination (`stars=3` (int), real pizza, valid owner token).
- **Non-base Tests:** Each non-base block modifies exactly one characteristic while holding the remaining characteristics at their base values:
  - C1: 2 non-base blocks (tested in `test_stars_out_of_range`)
  - C2: 3 non-base blocks (`test_stars_decimal_type_is_refused`, `test_stars_text_type_is_refused`, `test_stars_missing_is_refused`)
  - C3: 1 non-base block (`test_pizza_does_not_exist_is_refused`)
  - C4: 2 non-base blocks (`test_token_missing_is_refused`, `test_token_wrong_length_is_refused`)
- **Total Tests for Base Choice Coverage:** $1 + 2 + 3 + 1 + 2 = 9$ tests in `test_create_rating.py`.
