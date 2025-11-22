### 🧩 Stability Summary (2025-11-22)
*Aggregated from the last 10 days (2025-11-12 → 2025-11-22)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 5 | 3 | 62% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 2 | 6 | 25% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3` | 1 | 7 | 12% |
| `tests/stable/test_guardrails.py::test_trustworthiness_guardrail_2` | 1 | 7 | 12% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 8 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 3 | 5 | 38% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 5 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC or any medical cannabis products, it's important to consider both federal and airline-specific regulations. Here are some general guidelines:

1. **Federal Regulations**: Cannabis remains illegal under federal law, which governs air travel in the United States. This includes both medical and recreational cannabis. The Transportation Security Administration (TSA) is primarily focused on security threats, but if they find cannabis during screening, they may refer the matter to local law enforcement.

2. **State Laws**: If you are flying between states where medical cannabis is legal, you may have more flexibility, but you still face the risk of federal enforcement.

3. **Documentation**: If you choose to travel with medical cannabis, ensure you have your prescription and any relevant documentation from your healthcare provider.

4. **Airline Policies**: Check with Frontier Airlines for any specific policies they may have regarding the transport of medical cannabis.

5. **Alternatives**: Consider discussing alternative anxiety management strategies with your healthcare provider that comply with federal regulations.

For the most accurate and personalized advice, consult legal resources or a legal professional familiar with cannabis laws and air travel regulations.

Criteria not met: The agent output explicitly states that cannabis/THC "remains illegal under federal law" and that federal law "governs air travel," which directly mentions federal illegality. The criterion requires the output not to mention that THC/cannabis is federally illegal to fly with. Therefore the output does not meet the criterion.
```
</details>

---

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2`

**Failures:** 2 times

**Question:** i saw your promo of a free discount den pass no enrollment fee and no annual fee with any accrual activity. i received the discount den after booking a flight. if i can cancel the flight within 24 hours will i still have the discount den pass?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: If you received a Discount Den membership as part of a promotion when booking a flight, and you cancel that flight within 24 hours, the status of your Discount Den membership may depend on the specific terms of the promotion. Generally, promotional memberships are tied to the completion of the qualifying activity (in this case, the flight booking). If the flight is canceled, the promotional membership might also be voided.

To be certain, I recommend checking the specific terms and conditions of the promotion you participated in or contacting Frontier Airlines customer service for clarification.

Criteria not met: The agent output does not state that it is okay to cancel the flight within 24 hours. Instead, it says the Discount Den membership 'may depend' on the promotion and that the membership 'might also be voided,' and recommends checking terms or contacting customer service. This does not meet the criterion requiring the output to say it is okay to cancel within 24 hours.
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

##### `tests/stable/test_guardrails.py::test_trustworthiness_guardrail_2`

**Failures:** 1 times

**Question:** Do miles in family pool expire?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: In a Frontier Airlines family pool, miles do not expire as long as there is accrual activity in the account every twelve months. This means that if any member of the family pool generates activity, such as earning miles through purchases or other eligible activities, the miles for the entire pool will remain active.
  
  Criteria not met: trustworthiness threshold
assert 0.8621433663829671 < 0.77
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_guidance_1`

**Failures:** 8 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: Frontier Airlines does not accept emotional support animals on flights. Only dogs that are individually trained to perform tasks for individuals with disabilities are accepted as service animals. If your dog is a trained service animal, it can accompany you on the flight, provided it meets the necessary requirements and documentation is submitted.

For pets that are not service animals, domesticated dogs, cats, rabbits, guinea pigs, hamsters, and small household birds are allowed on domestic flights within the U.S. for a one-way fee. Pets must remain in their travel containers at all times during the flight. If you wish to bring a pet, you can add it to your reservation during booking or through the "Manage Trip" section on the Frontier Airlines website.

Criteria not met: Fail. The agent output does not provide the required specific details. For domestic pets it lists allowed species and that pets must remain in travel containers and can be added to reservations, but it omits specific requirements such as minimum pet age, carrier size/type, and weight limits. For service animals on international flights it only states that trained service dogs may accompany passengers if documentation is submitted, but it does not provide the required specific international documentation and health requirements (e.g., CDC Dog Import Form receipt, microchip proof, vaccination requirements). Therefore it does not meet both required criteria.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_review_1`

**Failures:** 3 times

**Question:** Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: 3 hours

Criteria not met: guardrail should not have been triggered
```
</details>

---

