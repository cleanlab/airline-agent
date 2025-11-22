### 🧩 Stability Summary (2025-11-22)
*Aggregated from the last 10 days (2025-11-12 → 2025-11-22)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 4 | 2 | 67% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 1 | 5 | 17% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3` | 1 | 5 | 17% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 6 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 2 | 4 | 33% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 4 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC, it's important to consider both TSA regulations and the airline's policies. Here are some general guidelines:

1. **TSA Regulations**: The TSA allows passengers to travel with medications in both carry-on and checked baggage. However, marijuana and certain cannabis-infused products, including some cannabidiol (CBD) oil, remain illegal under federal law, except for products that contain no more than 0.3% THC on a dry weight basis or are approved by the FDA.

2. **Prescription Documentation**: If you have a prescription for THC, it is advisable to carry documentation, such as a doctor's note or the prescription itself, to verify its medical necessity.

3. **State Laws**: Consider the laws of the states you are traveling to and from, as they may have different regulations regarding medical marijuana.

4. **Airline Policies**: While Frontier Airlines does not have specific policies listed for carrying THC, it is generally recommended to check with the airline directly if you have any concerns or need clarification.

For your specific situation, ensure you have your prescription documentation with you and be prepared to explain its medical necessity if asked. If you have further questions or need specific guidance, contacting Frontier Airlines directly or consulting with legal experts on state and federal regulations might be beneficial.

Criteria not met: The agent output explicitly states that “marijuana and certain cannabis-infused products... remain illegal under federal law,” which mentions the federal illegality of THC/cannabis. This violates the criterion prohibiting such mention.
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

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3`

**Failures:** 1 times

**Question:** If both of my small bags fit completely under the seat in front of me without taking any extra space, that counts as one personal item, correct?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: For Frontier Airlines, a personal item must be no larger than 14” H x 18” W x 8” D, including handles, wheels, and straps. If both of your small bags fit completely under the seat in front of you and together do not exceed these dimensions, they would count as one personal item. However, if combined they exceed these dimensions, they would not qualify as a single personal item.
  
  Criteria not met: trustworthiness threshold
assert 0.8276758670071535 < 0.77
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_guidance_1`

**Failures:** 6 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: Frontier Airlines does not accept emotional support animals on their flights. Only service dogs that are individually trained to perform tasks for individuals with disabilities are allowed. If your dog is a service animal, you will need to provide the necessary documentation. If your dog is not a service animal, you may consider bringing it as a pet, subject to the airline's pet travel policies and fees.

Criteria not met: The agent output does not include specific requirements for pets on domestic flights—no details on pet age minimums, carrier size/type, or weight limits are given. It also does not include specific requirements for service animals on international flights—no documentation rules, CDC Dog Import Form receipt, microchip proof, or vaccination requirements are provided. Therefore it does not meet the criteria requiring both types of specific requirements together.
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

