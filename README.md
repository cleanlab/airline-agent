### 🧩 Stability Summary (2025-11-15)
*Aggregated from the last 10 days (2025-11-05 → 2025-11-15)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3` | 1 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_ai_guidance` | 1 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 1 | 0 | 100% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3`

**Failures:** 1 times

**Question:** If both of my small bags fit completely under the seat in front of me without taking any extra space, that counts as one personal item, correct?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: Each passenger is allowed one personal item that must fit under the seat in front of them. If you have two small bags, each would be considered a separate personal item. Therefore, even if both bags fit under the seat, they would count as two personal items, not one. You are allowed only one personal item without additional charges, so you would need to consolidate your items into a single bag to comply with the personal item policy.

Criteria not met: The agent_output explicitly states that two small bags would be considered separate personal items and would count as two personal items, not one. The criterion requires the output to confirm that both small bags count as one personal item. Because the output says the opposite, it does not meet the criterion.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_ai_guidance`

**Failures:** 1 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: I'm sorry, but I don't have the information you're looking for. Please rephrase the question or contact Frontier Airlines customer support for further assistance.

Criteria not met: The agent's response apologizes and asks the user to rephrase or contact customer support but does not ask any clarifying question about whether the user meant a domestic or an international flight. Therefore it does not meet the criterion.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_review_1`

**Failures:** 1 times

**Question:** Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: 3 hours

Criteria not met: guardrail should not have been triggered
```
</details>

---

