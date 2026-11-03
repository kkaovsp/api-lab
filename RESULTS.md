# API lab results

## Part 0
- Step 0.1, the number of pizza names: 18
- Step 0.3, status code of the request without a token: 401
- Step 0.4, the name of your pizza: A Sour Quattro Stagioni
- Step 0.12, results of the three runs without a session (optional): Run 1: PASSED, Run 2: PASSED, Run 3: FAILED (AssertionError: 401 == 200, flaky due to missing load balancer sticky session cookie)
- Step 0.16, blocks of "how many of the three tools are excluded":
  - Block 0: 0 tools excluded (`[]`)
  - Block 1: 1 tool excluded (`["Knife"]`, `["Scissors"]`, `["Pizza cutter"]`)
  - Block 2: 2 tools excluded (`["Knife", "Scissors"]`)
  - Block 3: 3 tools excluded / all tools (`["Knife", "Pizza cutter", "Scissors"]`)

## Defect report
- Title: Excluding all tools causes 500 Internal Server Error instead of 400 Bad Request
- Request: POST https://quickpizza.grafana.com/api/pizza with body `{"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}` and Authorization header with valid token
- Expected result: HTTP status 400 Bad Request with JSON error message `{"error": "..."}` explaining that no pizza can satisfy the restrictions
- Actual result: HTTP status 500 Internal Server Error with an empty response body
- Severity: High (Server crash / unhandled backend exception, breaks API contract and provides no actionable feedback to client applications)

## Part A
- Step A4, status codes when the other user reads, changes and deletes:
  - Read (GET /api/ratings/{id}): 404
  - Change (PUT /api/ratings/{id}): 400
  - Delete (DELETE /api/ratings/{id}): 400

## Part B
1. Two kinds of failure found by real server API tests that stubbed unit tests cannot:
   - Network and infrastructure integration failures, such as load balancer session cookie routing issues (`AWSALB`), reverse proxy misconfigurations, TLS/SSL connection failures, and header propagation issues.
   - Database and schema integration errors, such as database foreign key constraint violations, JSON serialization/unmarshaling type mismatches into backend Go structs, and backend crashes (500) caused by unexpected live inputs.
   One reason to write unit tests with stubs as well:
   - Stubbed unit tests execute in milliseconds, run deterministically offline without network dependencies or flakiness, and can simulate rare edge-case error conditions (e.g. disk full, downstream service timeout, network partition) that are difficult or unsafe to produce against live servers.

2. Why every test creates its own user:
   - Test isolation and independence. Reusing a shared user or the public token means concurrent test runs (or other students' tests) would mutate the same database records (such as deleting or modifying ratings), leading to race conditions and flaky tests. Generating a unique user per test ensures a predictable, clean state.
   Application to Project 2:
   - In Project 2 (shared shop or hotel), each test suite should dynamically provision its own unique user entity (e.g. `group-<uuid>`) or isolated cart/booking session rather than sharing fixed credentials, guaranteeing tests run without interfering with other groups.

3. Why tests send every request through one session:
   - QuickPizza operates multiple backend instances behind an AWS Application Load Balancer. The instances maintain local user state and rely on sticky sessions via `AWSALB` and `AWSALBCORS` cookies. Using `requests.Session()` automatically persists and transmits these cookies across subsequent requests, ensuring every request from a test reaches the same backend instance.
   What happened in Step 0.12:
   - In our three runs without a session (`test_no_session.py`), Run 1 passed, Run 2 passed, and Run 3 failed with `401 Unauthorized` during login. Without sticky session cookies, the load balancer routed the login request to a different backend server that had no record of the user created just moments before.

4. Excluded tools defect analysis:
   - Block that revealed the defect: Block 3 (all 3 tools excluded: `["Knife", "Pizza cutter", "Scissors"]`).
   - Why 500 is worse than 400: Status 500 signals an unhandled crash inside the server and returns an empty body, leaving the client application unable to understand what failed or present helpful feedback to the user. Status 400 with a clear JSON error message informs the client of invalid input parameters that cannot be satisfied.
   - Why keep as xfail: `@pytest.mark.xfail(strict=True)` tracks the known defect in the test suite without breaking continuous integration (CI) builds. With `strict=True`, pytest will alert the team if a server update fixes the defect (turning it into an unexpected pass / XPASS), indicating the marker should be removed.

5. Test count calculation for Step A1 model:
   - Characteristics and blocks:
     - C1 (Value of stars): 3 blocks (below 1, 1 to 5 [base], above 5)
     - C2 (Type of stars): 4 blocks (whole number [base], decimal, text, missing)
     - C3 (Pizza): 2 blocks (exists [base], does not exist)
     - C4 (Token): 3 blocks (user's own [base], none, wrong length)
   - Base Choice Coverage:
     - 1 base test covering all base blocks simultaneously.
     - For each characteristic, vary one block away from base at a time:
       $(3 - 1) + (4 - 1) + (2 - 1) + (3 - 1) = 2 + 3 + 1 + 2 = 8$ additional tests.
     - Total = $1 + 8 = 9$ tests.
   - All Combinations Coverage:
     - Cartesian product of all blocks:
       $3 \times 4 \times 2 \times 3 = 72$ tests.

6. Access control status codes and defect evaluation:
   - Status codes obtained: Read (GET): `404`, Change (PUT): `400`, Delete (DELETE): `400`.
   - Expected status codes: REST conventions recommend returning `403 Forbidden` (caller is authenticated but not authorized to access/modify another user's resource) or consistently returning `404 Not Found` (to avoid disclosing whether a resource ID exists).
   - Defect evaluation: Yes, this difference is a defect. Returning `400 Bad Request` with `"rating ID ... not found"` for PUT and DELETE is semantically incorrect according to HTTP specifications (400 represents invalid client syntax, not authorization/existence issues). Furthermore, returning 404 for GET but 400 for PUT/DELETE on the same unauthorized resource is inconsistent.

7. Made-up token inspection (`madeup.txt`):
   - What comes back: HTTP status `200 OK` and a JSON array containing all ratings stored across all users in the system.
   - Defect evaluation: Yes, this is a critical security vulnerability (Broken Object Level Authorization / Authentication Bypass).
   - Stranger exploit on real system: An attacker could bypass authentication by presenting any arbitrary 16-character string, scrape private customer ratings, harvest user and pizza IDs, and potentially discover internal data or perform IDOR attacks.

8. Comparison between API tests and Web UI tests:
   - API tests check better: Direct inspection of HTTP status codes, response headers, schema data types, raw boundary inputs (bypassing client-side JavaScript validation), and backend error messages, while executing much faster and with greater stability.
   - Web page tests check exclusively: Visual layout and rendering (CSS styling, responsive design across mobile/desktop), DOM interactions, client-side JavaScript execution, browser compatibility, and real end-user visual/interactive workflows.
