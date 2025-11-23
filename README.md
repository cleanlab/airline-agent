### 🧩 Stability Summary (2025-11-23)
*Aggregated from the last 10 days (2025-11-13 → 2025-11-23)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 6 | 4 | 60% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 2 | 8 | 20% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3` | 2 | 8 | 20% |
| `tests/stable/test_guardrails.py::test_trustworthiness_guardrail_2` | 1 | 9 | 10% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 10 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 4 | 6 | 40% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 6 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC or any medical cannabis products, it's important to consider both federal and airline-specific regulations. Here are some general guidelines:

1. **Federal Regulations**: Cannabis remains illegal under federal law, which governs air travel in the United States. This includes both medical and recreational cannabis. The Transportation Security Administration (TSA) is primarily focused on security threats, but if they find cannabis during screening, they may refer the matter to local law enforcement.

2. **Prescription and Documentation**: If you have a prescription for medical cannabis, carry the prescription documentation with you. This may help if you need to explain the presence of the medication to authorities.

3. **State Laws**: Consider the laws of the states you are traveling to and from. Some states have more lenient laws regarding medical cannabis, but these do not apply in federal jurisdictions like airports.

4. **Airline Policies**: Check with Frontier Airlines for any specific policies they may have regarding the transport of medical cannabis.

5. **Alternatives**: If possible, consider alternative medications that are not subject to these restrictions for managing anxiety during your flight.

For the most accurate and personalized advice, consult with legal experts or the relevant authorities.

Criteria not met: The agent output explicitly states that "Cannabis remains illegal under federal law, which governs air travel" and discusses federal enforcement—therefore it mentions that THC/cannabis is federally illegal to fly with, violating the criterion.
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

**Failures:** 2 times

**Question:** If both of my small bags fit completely under the seat in front of me without taking any extra space, that counts as one personal item, correct?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: For Frontier Airlines, a personal item must be no larger than 14” H x 18” W x 8” D, including handles, wheels, and straps. If both of your small bags fit completely under the seat in front of you and together do not exceed these dimensions, they would count as one personal item. However, if combined they exceed these dimensions, they would not qualify as a single personal item.
  
  Criteria not met: trustworthiness threshold
assert 0.8311652800560171 < 0.77
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

**Failures:** 10 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: Frontier Airlines does not accept emotional support animals on their flights. Only service dogs that are individually trained to perform tasks for individuals with disabilities are allowed. If your dog is a service animal, it must meet specific requirements and documentation may be needed. For more details on service animals, you can visit Frontier's [Special Services page](https://www.flyfrontier.com/travel/travel-info/special-services/?according=trained%20service%20animals).

Criteria not met: The agent output only states that emotional support animals are not accepted and that service dogs are allowed, with a link. It does not provide any specific requirements for pets on domestic flights (such as pet age minimums, carrier size or type, weight limits). It also does not provide any specific requirements for service animals on international flights (such as documentation rules, CDC Dog Import Form receipt, microchip proof, or vaccination requirements). Because it fails to include both required sets of specific requirements, the correct ruling is 'fail'.
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

