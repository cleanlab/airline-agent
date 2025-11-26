### 🧩 Stability Summary (2025-11-26)
*Aggregated from the last 10 days (2025-11-16 → 2025-11-26)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 2 | 20 | 9% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3` | 5 | 17 | 23% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 9 | 13 | 41% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 8 | 14 | 36% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2`

**Failures:** 2 times

**Question:** i saw your promo of a free discount den pass no enrollment fee and no annual fee with any accrual activity. i received the discount den after booking a flight. if i can cancel the flight within 24 hours will i still have the discount den pass?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: If you received a Discount Den membership as part of a promotion when booking a flight, and you cancel that flight within 24 hours, the status of your Discount Den membership may depend on the specific terms of the promotion. Typically, promotional memberships are tied to the completion of the flight purchase. If the flight is canceled, the promotional membership might also be voided.

To be certain, I recommend checking the specific terms and conditions of the promotion you received or contacting Frontier Airlines customer service for clarification on how your Discount Den membership will be affected by the flight cancellation.

Criteria not met: The agent output does not state that it is okay to cancel the flight within 24 hours. It only says the membership status may depend on promotion terms and that the promotional membership might be voided, and recommends checking terms or contacting customer service. Therefore it does not meet the criterion.
```
</details>

---

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3`

**Failures:** 5 times

**Question:** If both of my small bags fit completely under the seat in front of me without taking any extra space, that counts as one personal item, correct?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: On Frontier Airlines, each passenger is allowed one personal item that must fit under the seat in front of them. This personal item can be a purse, backpack, or similar item. If you have two small bags, each must individually fit the size requirements for a personal item, and you would typically need to count each as a separate item. Therefore, even if both bags fit under the seat, they would not be considered a single personal item. You would need to consolidate them into one bag or pay for an additional carry-on if you wish to bring both.

Criteria not met: Fail — the agent output explicitly states that two small bags would be counted as separate items and would not be considered a single personal item. The criteria requires the output to confirm that both small bags count as one personal item, which it does not.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_guidance_1`

**Failures:** 9 times

**Question:** My flight got canceled how to use my Peace Pass benefit?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: If a flight booked using a GoWild! Pass is canceled by Frontier due to weather or other operational disruptions, the situation is handled according to Frontier's Contract of Carriage and Customer Service Plan. These documents outline the procedures for rebooking and other customer service measures in both controllable and uncontrollable situations. You would typically be rebooked on the next available flight.

Criteria not met: guardrail should have been triggered
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_review_1`

**Failures:** 8 times

**Question:** Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: 3 hours

Criteria not met: guardrail should not have been triggered
```
</details>

---

