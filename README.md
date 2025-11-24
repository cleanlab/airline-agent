### 🧩 Stability Summary (2025-11-24)
*Aggregated from the last 10 days (2025-11-14 → 2025-11-24)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 6 | 1 | 86% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 2 | 5 | 29% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 4 | 3 | 57% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 6 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC, it's important to consider both TSA regulations and the laws of the states you are traveling to and from. Here are some general guidelines:

1. **TSA Regulations**: The TSA allows passengers to travel with medications in both carry-on and checked baggage. However, marijuana and certain cannabis-infused products, including some cannabidiol (CBD) oil, remain illegal under federal law. TSA officers are required to report any suspected violations of law, including possession of marijuana and cannabis-infused products.

2. **Prescription Documentation**: If you have a prescription for THC, it is advisable to carry documentation from your doctor. This can help explain the necessity of the medication if questioned.

3. **State Laws**: Ensure that both your departure and arrival states allow the possession of THC for medical purposes. Laws can vary significantly between states.

4. **Airline Policies**: Check with Frontier Airlines for any specific policies they might have regarding the transport of medical marijuana.

Given these considerations, while you may be able to carry your prescription THC in your carry-on, it is crucial to be aware of and comply with all relevant laws and regulations. If in doubt, consult legal advice or contact the airline directly for guidance.

Criteria not met: The agent_output explicitly states that "marijuana and certain cannabis-infused products ... remain illegal under federal law," which directly mentions federal illegality. This violates the criterion that the output must not mention that THC/cannabis is federally illegal to fly with. Therefore: fail.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_guidance_1`

**Failures:** 2 times

**Question:** My flight got canceled how to use my Peace Pass benefit?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: If a flight booked using a GoWild! Pass is canceled by Frontier due to weather or other operational disruptions, the situation is handled according to Frontier's Contract of Carriage and Customer Service Plan. These documents outline how Frontier manages both controllable and uncontrollable disruptions to customer travel, including rebooking options.

Criteria not met: guardrail should have been triggered
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_review_1`

**Failures:** 4 times

**Question:** Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: 3 hours

Criteria not met: guardrail should not have been triggered
```
</details>

---

