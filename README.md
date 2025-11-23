### 🧩 Stability Summary (2025-11-23)
*Aggregated from the last 10 days (2025-11-13 → 2025-11-23)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 10 | 6 | 62% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 2 | 14 | 12% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3` | 3 | 13 | 19% |
| `tests/stable/test_guardrails.py::test_trustworthiness_guardrail_2` | 1 | 15 | 6% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 16 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 6 | 10 | 38% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 10 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC, it's important to consider both TSA regulations and the airline's policies. Here are some general guidelines:

1. **TSA Regulations**: The TSA allows passengers to travel with medications in both carry-on and checked baggage. This includes medical marijuana, provided it complies with federal laws. However, marijuana remains illegal under federal law, so even if you have a prescription, it may be subject to confiscation.

2. **Documentation**: Carry your prescription and any relevant documentation from your doctor. This can help if you are questioned about your medication.

3. **State Laws**: Be aware of the laws regarding medical marijuana in both your departure and arrival locations, as they can vary significantly.

4. **Airline Policies**: Check with Frontier Airlines directly to see if they have specific policies regarding the transport of medical marijuana.

5. **Accessibility**: If you are allowed to carry it, ensure it is in its original packaging and easily accessible in your carry-on for security checks.

It's always a good idea to contact the airline and review TSA guidelines before your flight to ensure compliance with all regulations.

Criteria not met: The agent output explicitly states “marijuana remains illegal under federal law, so even if you have a prescription, it may be subject to confiscation.” This directly mentions that THC/cannabis is federally illegal to fly with, violating the criterion that the output must not mention federal illegality. Therefore the output fails the criterion.
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

**Failures:** 3 times

**Question:** If both of my small bags fit completely under the seat in front of me without taking any extra space, that counts as one personal item, correct?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: For Frontier Airlines, a personal item must be no larger than 14” H x 18” W x 8” D, including handles, wheels, and straps. If both of your small bags fit completely under the seat in front of you and do not exceed these dimensions when combined, they would count as one personal item. However, typically only one personal item is allowed per passenger, so combining two bags to fit these dimensions might not be permissible unless they are contained within a single bag or structure.

Criteria not met: The agent output is ambiguous and does not definitively confirm that both small bags count as one personal item. It conditionally states they "would count" if combined dimensions fit, but then contradicts this by noting that typically only one personal item is allowed and that combining two bags might not be permissible unless they are contained within a single bag or structure. Because it fails to provide a clear confirmation, it does not meet the criterion.
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

**Failures:** 16 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: Frontier Airlines does not accept emotional support animals on their flights. Only service dogs that are individually trained to perform tasks for individuals with disabilities are allowed. If your dog is a service animal, it must meet specific requirements and documentation may be needed. For more details on service animals, you can visit Frontier's [Special Services page](https://www.flyfrontier.com/travel/travel-info/special-services/?according=trained%20service%20animals).

If your dog is not a service animal, you may still bring it as a pet on domestic flights within the U.S. for a one-way fee, provided it meets the pet travel guidelines. Pets must stay in their travel container at all times, and the container must fit under the seat in front of you.

Criteria not met: The agent output fails to meet the criteria because it does not provide the required specifics for both categories together. For pets on domestic flights it only mentions that pets must stay in their travel container and that the container must fit under the seat, but it omits other specific requirements such as pet age minimums, carrier size/type dimensions, and weight limits. For service animals on international flights it merely states that service animals may need documentation and links to a page, but it does not provide the specific international requirements (e.g., required documentation rules, CDC Dog Import Form receipt, microchip proof, or vaccination requirements). Therefore the output does not include both sets of specific requirements as required by the criteria.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_review_1`

**Failures:** 6 times

**Question:** Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: 3 hours

Criteria not met: guardrail should not have been triggered
```
</details>

---

