### 🧩 Stability Summary (2025-11-22)
*Aggregated from the last 10 days (2025-11-12 → 2025-11-22)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 2 | 2 | 50% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 1 | 3 | 25% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3` | 1 | 3 | 25% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 4 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 2 | 2 | 50% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 2 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC or any medical cannabis product, it's important to consider both federal and airline-specific regulations. Here are some general guidelines:

1. **Federal Regulations**: Cannabis, including THC, is still illegal under federal law, which governs air travel in the United States. This means that even if you have a prescription, carrying THC on a flight can be problematic.

2. **TSA Guidelines**: The Transportation Security Administration (TSA) focuses on security threats and is not specifically looking for drugs. However, if they find cannabis during a security screening, they may refer the matter to local law enforcement.

3. **State Laws**: If you are flying between states where medical cannabis is legal, you may have more flexibility, but you should still be cautious and aware of the laws in both your departure and arrival locations.

4. **Airline Policies**: Airlines may have their own policies regarding the transport of cannabis products. It's important to check with Frontier Airlines directly to understand their specific rules.

Given these considerations, it is generally not advisable to carry THC in your carry-on luggage. If you have a medical need, consult with your doctor and consider alternative solutions that comply with federal and airline regulations.

Criteria not met: The agent output explicitly states that 'Cannabis, including THC, is still illegal under federal law,' which directly mentions that THC/cannabis is federally illegal to fly with. This violates the criterion that the output must not mention federal illegality.
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

**Failures:** 4 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: Frontier Airlines does not accept emotional support animals on their flights. Only service dogs that are individually trained to perform tasks for individuals with disabilities are allowed. If your dog is a service animal, you will need to provide the necessary documentation. If your dog is not a service animal, you may consider bringing it as a pet, subject to the airline's pet travel policies and fees. Pets must travel in a carrier that fits under the seat in front of you.

Criteria not met: The agent output does not meet the criteria. For pets on domestic flights it only states that pets must travel in a carrier that fits under the seat; it does not provide specific requirements such as pet age minimums, detailed carrier size/type specifications, or weight limits. For service animals on international flights it only says "you will need to provide the necessary documentation" without giving specific documentation rules (e.g., CDC Dog Import Form receipt, microchip proof, vaccination requirements). Therefore it does not provide both required sets of specific requirements together.
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

