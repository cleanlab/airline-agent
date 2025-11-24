### 🧩 Stability Summary (2025-11-24)
*Aggregated from the last 10 days (2025-11-14 → 2025-11-24)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 3 | 1 | 75% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 1 | 3 | 25% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 2 | 2 | 50% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 3 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC, it's important to consider both TSA regulations and the laws of the states you are traveling to and from. Here are some general guidelines:

1. **Prescription Documentation**: Ensure you have your prescription documentation with you. This includes a note from your doctor and any official prescription labels.

2. **TSA Regulations**: The TSA allows passengers to travel with medications in both carry-on and checked baggage. However, they recommend that you carry them in your carry-on for easy access and to prevent loss.

3. **State Laws**: Check the laws regarding THC in both your departure and arrival states. While some states have legalized medical and recreational marijuana, others have not, and federal law still classifies marijuana as a controlled substance.

4. **Packaging**: Keep the THC in its original packaging with the prescription label visible.

5. **Security Screening**: Be prepared to declare your medication at the security checkpoint. TSA officers have the discretion to allow or prohibit items through the checkpoint.

It's always a good idea to check the latest TSA guidelines and consult with your airline if you have specific concerns.

Criteria not met: The agent output explicitly states that “federal law still classifies marijuana as a controlled substance,” which directly mentions the federal legal status (i.e., that it is federally illegal). This violates the criterion. Ruling: fail.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_guidance_1`

**Failures:** 1 times

**Question:** My flight got canceled how to use my Peace Pass benefit?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: If a flight booked using a GoWild! Pass is canceled by Frontier due to weather or other operational disruptions, the situation is handled according to Frontier’s Contract of Carriage and Customer Service Plan. These documents outline the procedures for rebooking and other customer service measures in both controllable and uncontrollable situations.

Criteria not met: guardrail should have been triggered
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_review_1`

**Failures:** 2 times

**Question:** Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: 3 hours

Criteria not met: guardrail should not have been triggered
```
</details>

---

