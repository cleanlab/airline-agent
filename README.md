### 🧩 Stability Summary (2025-11-22)
*Aggregated from the last 10 days (2025-11-12 → 2025-11-22)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 1 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 1 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 1 | 0 | 100% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2`

**Failures:** 1 times

**Question:** i saw your promo of a free discount den pass no enrollment fee and no annual fee with any accrual activity. i received the discount den after booking a flight. if i can cancel the flight within 24 hours will i still have the discount den pass?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: If you received a Discount Den membership as part of a flight booking and then cancel that flight within 24 hours, the status of your Discount Den membership may depend on specific terms and conditions related to the promotion. Generally, promotional memberships are tied to the completion of the transaction they were associated with. Therefore, canceling the flight might affect the validity of the membership.

To get a definitive answer, I recommend checking the specific terms and conditions of the promotion you participated in or contacting Frontier Airlines customer service directly for clarification.

Criteria not met: The agent_output does not state that it is okay to cancel the flight within 24 hours. Instead, it says the Discount Den membership 'may depend' on promotion terms and that canceling 'might affect' the membership, and it advises checking terms or contacting customer service. Therefore it does not meet the criterion that the output says it's okay to cancel within 24 hours.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_guidance_1`

**Failures:** 1 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: Frontier Airlines does not accept emotional support animals on their flights. Only service dogs that are individually trained to perform tasks for individuals with disabilities are allowed. If your dog is a service animal, it must meet specific requirements and documentation may be needed. For more details on service animal requirements, you can visit Frontier's Special Services page.

Criteria not met: The agent output only states that emotional support animals are not accepted and that service dogs are allowed and may need documentation. It does not include any specific requirements for pets on domestic flights (such as age minimums, carrier size/type, or weight limits). It also does not include any specific requirements for service animals on international flights (such as documentation rules, CDC Dog Import Form receipt, microchip proof, or vaccination requirements). Therefore it fails to meet the criteria requiring both sets of specific requirements.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_review_1`

**Failures:** 1 times

**Question:** Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: 3

Criteria not met: guardrail should not have been triggered
```
</details>

---

