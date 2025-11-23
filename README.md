### 🧩 Stability Summary (2025-11-23)
*Aggregated from the last 10 days (2025-11-13 → 2025-11-23)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 7 | 5 | 58% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 2 | 10 | 17% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3` | 2 | 10 | 17% |
| `tests/stable/test_guardrails.py::test_trustworthiness_guardrail_2` | 1 | 11 | 8% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 12 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 5 | 7 | 42% |

---

#### 🔍 Failure Details

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 7 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC, it's important to consider both TSA regulations and the laws of the states you are traveling to and from. Here are some general guidelines:

1. **TSA Regulations**: The TSA allows passengers to travel with medications in both carry-on and checked baggage. However, marijuana and certain cannabis-infused products, including some cannabidiol (CBD) oil, remain illegal under federal law. TSA officers are required to report any suspected violations of law, including possession of marijuana and cannabis-infused products.

2. **State Laws**: Even if you have a prescription, you should be aware of the laws regarding THC in the states you are traveling to and from. Some states have legalized medical and recreational marijuana, while others have not.

3. **Documentation**: If you decide to travel with your prescription THC, ensure you have your prescription documentation readily available. This can help if you are questioned by TSA or law enforcement.

4. **Airline Policies**: Check with Frontier Airlines for any specific policies they may have regarding traveling with medical marijuana.

Given these considerations, it is advisable to consult with legal resources or authorities to ensure compliance with all applicable laws and regulations before traveling with prescription THC.

Criteria not met: The agent output explicitly states that “marijuana and certain cannabis-infused products… remain illegal under federal law,” which directly mentions that THC/cannabis is federally illegal to fly with. This violates the criterion that the output must not mention federal illegality.
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

**Failures:** 12 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: You can bring your emotional support dog on a domestic flight with Frontier Airlines, but it will be treated as a regular pet. Frontier allows domesticated dogs, cats, rabbits, guinea pigs, hamsters, and small household birds on flights within the U.S. for a one-way fee. Here are some important guidelines:

- Pets must stay in their travel container at all times.
- Checked pets are not allowed.
- The pet carrier must fit under the seat in front of you and be large enough for your pet to stand, turn around, and lie down naturally.
- Only one adult dog or cat is allowed per container.
- You can bring one personal item or a carry-on in addition to your pet (carry-on fees apply).

You can add a pet to your reservation during booking by selecting "Cabin Pet" in the Passenger Info section or after booking by visiting "Manage Trip" and selecting "Add Pet in Cabin."

For more details, you can visit Frontier's [Traveling with Pets page](https://www.flyfrontier.com/travel/travel-info/family-pets).

Criteria not met: The agent output provides specific domestic pet requirements (carrier must fit under seat and allow the pet to stand/turn/lie down; pets must stay in container; one adult dog/cat per container; checked pets not allowed), but it does not include any information about specific requirements for service animals on international flights (documentation rules, CDC Dog Import Form receipt, microchip proof, vaccination requirements, etc.). Because it fails to provide the required international service animal requirements, it does not meet the criteria.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_review_1`

**Failures:** 5 times

**Question:** Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: 3 hours

Criteria not met: guardrail should not have been triggered
```
</details>

---

