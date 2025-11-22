### 🧩 Stability Summary (2025-11-22)
*Aggregated from the last 10 days (2025-11-12 → 2025-11-22)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 1 | 1 | 50% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 1 | 1 | 50% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 2 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 1 | 1 | 50% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 1 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC, it's important to consider both TSA regulations and the airline's policies. Here are some general guidelines:

1. **TSA Regulations**: The TSA allows passengers to travel with medications in both carry-on and checked baggage. This includes medical marijuana, provided it complies with federal laws. However, marijuana remains illegal under federal law, so even if you have a prescription, it may be subject to confiscation.

2. **Documentation**: Carry your prescription and any relevant documentation from your doctor. This can help if you are questioned by security or airline staff.

3. **State Laws**: Be aware of the laws regarding medical marijuana in both your departure and arrival locations, as they can vary significantly.

4. **Airline Policies**: Check with Frontier Airlines directly to see if they have specific policies regarding the transport of medical marijuana.

5. **Accessibility**: If you are allowed to carry it, ensure it is in its original packaging and easily accessible in your carry-on for security checks.

For the most accurate and personalized advice, consider contacting Frontier Airlines and reviewing TSA guidelines before your flight.

Criteria not met: The agent output explicitly states "marijuana remains illegal under federal law, so even if you have a prescription, it may be subject to confiscation." This mentions that THC/cannabis is federally illegal to fly with, which violates the criterion. Therefore the output fails.
```
</details>

---

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

**Failures:** 2 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: Frontier Airlines does not accept emotional support animals on their flights. Only dogs that are individually trained to work or perform tasks for the benefit of a qualified individual with a disability are accepted as service animals. This includes psychiatric service dogs. If you have a service dog, you will need to provide the necessary documentation to travel with your dog.

If your dog does not qualify as a service animal, you may be able to bring it as a pet in the cabin on domestic flights within the U.S. for a fee. The pet must remain in a travel container that fits under the seat in front of you. If you need more information on traveling with pets, please let me know!

Criteria not met: The agent output fails to meet the criteria. For pets on domestic flights it only mentions that a pet must remain in a travel container that fits under the seat and that a fee applies; it does not provide the required specific details such as pet age minimums, explicit carrier size/type dimensions, or weight limits. For service animals on international flights it merely states that documentation is needed and that only trained dogs are accepted; it does not provide the required specific international documentation and health requirements (e.g., CDC Dog Import Form receipt, microchip proof, vaccination requirements, or other country-specific entry rules). Because both sets of specific requirements were not provided together, the output does not meet the criteria.
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

