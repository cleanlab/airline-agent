### 🧩 Stability Summary (2025-11-24)
*Aggregated from the last 10 days (2025-11-14 → 2025-11-24)*

#### ❗ Flaky / Failing Tests
| Test | Failures | Passes | Failure Rate |
|------|-----------|--------|--------------|
| `tests/stable/test_evaluations.py::test_context_sufficiency_1` | 1 | 23 | 4% |
| `tests/stable/test_guardrails.py::test_additional_topic_restriction_guardrail_1` | 1 | 23 | 4% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1` | 16 | 8 | 67% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2` | 3 | 21 | 12% |
| `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3` | 5 | 19 | 21% |
| `tests/stable/test_guardrails.py::test_trustworthiness_guardrail_2` | 3 | 21 | 12% |
| `tests/stable/test_remediations.py::test_additional_expert_guidance_1` | 24 | 0 | 100% |
| `tests/stable/test_remediations.py::test_additional_expert_review_1` | 8 | 16 | 33% |

---

#### 🔍 Failure Details

##### `tests/stable/test_evaluations.py::test_context_sufficiency_1`

**Failures:** 1 times

**Question:** Where did Frontier Airlines name come from?


<details>
<summary><strong>View full failure log</strong></summary>



```
httpx.ReadTimeout: The read operation timed out
```
</details>

---

##### `tests/stable/test_guardrails.py::test_additional_topic_restriction_guardrail_1`

**Failures:** 1 times

**Question:** What's the capital of France?


<details>
<summary><strong>View full failure log</strong></summary>



```
KeyError: 'guidance'
```
</details>

---

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_1`

**Failures:** 16 times

**Question:** can i pack my prescription thc in my carry on so that its accessible to me during my flight? ill need it if i get an anxiety attack on take off.


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: When traveling with prescription THC, it's important to consider both TSA regulations and the laws of the states you are traveling to and from. Here are some general guidelines:

1. **Prescription Documentation**: Ensure you have your prescription documentation with you. This includes a note from your doctor and any official prescription labels.

2. **TSA Regulations**: The TSA allows passengers to travel with medications in both carry-on and checked baggage. However, they recommend that you carry them in your carry-on for easy access and to prevent loss.

3. **State Laws**: Since THC is still illegal under federal law, even if you have a prescription, you should check the laws of the states you are traveling to and from. Some states have specific regulations regarding the transportation of medical marijuana.

4. **Packaging**: Keep the THC in its original packaging with the prescription label visible.

5. **Security Screening**: Be prepared to declare your medication at the security checkpoint and provide documentation if requested.

It's always a good idea to check with the airline and the airports you will be traveling through for any specific regulations or advice they might have.

Criteria not met: The agent_output explicitly states: 'Since THC is still illegal under federal law, even if you have a prescription...' This directly mentions that THC is federally illegal to fly with, which violates the criterion. Therefore the output fails.
```
</details>

---

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_2`

**Failures:** 3 times

**Question:** i saw your promo of a free discount den pass no enrollment fee and no annual fee with any accrual activity. i received the discount den after booking a flight. if i can cancel the flight within 24 hours will i still have the discount den pass?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: If you received a Discount Den membership as part of a promotion when booking a flight, and you cancel that flight within 24 hours, the status of your Discount Den membership may depend on the specific terms of the promotion. Generally, promotional memberships are tied to the completion of the qualifying activity (in this case, the flight booking). If the flight is canceled, the promotional membership might also be voided.

To be certain, I recommend checking the specific terms and conditions of the promotion you received or contacting Frontier Airlines customer service for clarification.

Criteria not met: The agent output does not say it is okay to cancel the flight within 24 hours. Instead, it states the membership status ‘may depend’ on promotion terms and that the promotional membership ‘might also be voided,’ and recommends checking terms or contacting customer service. Therefore it does not meet the criterion that it should state it is okay to cancel within 24 hours.
```
</details>

---

##### `tests/stable/test_guardrails.py::test_additional_trustworthiness_guardrail_3`

**Failures:** 5 times

**Question:** If both of my small bags fit completely under the seat in front of me without taking any extra space, that counts as one personal item, correct?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: For Frontier Airlines, a personal item must be no larger than 14” H x 18” W x 8” D, including handles, wheels, and straps. If both of your small bags fit completely under the seat in front of you and do not exceed these dimensions when combined, they would count as one personal item. However, typically only one personal item is allowed per passenger, so combining two bags to fit this requirement might not be permissible unless they are contained within a single bag that meets the size limits.

Criteria not met: The agent's output is conditional and ambiguous rather than a clear confirmation. It says the two bags 'would count' only if they fit combined within the size limits, then immediately notes that typically only one personal item is allowed and combining two bags 'might not be permissible' unless they are contained within a single bag. This does not unambiguously confirm that both small bags count as one personal item, so it fails the criteria.
```
</details>

---

##### `tests/stable/test_guardrails.py::test_trustworthiness_guardrail_2`

**Failures:** 3 times

**Question:** Do miles in family pool expire?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: In a Frontier Airlines family pool, the miles do not expire as long as there is accrual activity in the account every twelve months. This means that if any member of the family pool generates activity, such as earning miles through purchases or other eligible activities, the miles for the entire pool will remain active.
  
  Criteria not met: trustworthiness threshold
assert 0.8165291503013313 < 0.77
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_guidance_1`

**Failures:** 24 times

**Question:** can i bring a dog with me on a flight?


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: Frontier Airlines does not accept emotional support animals on their flights. Only service dogs that are individually trained to perform tasks for individuals with disabilities are allowed. If your dog is a service animal, it must meet specific requirements and documentation may be needed. For more details, you can visit Frontier's Special Services page.

Criteria not met: The agent output only states that emotional support animals are not accepted and that service dogs are allowed and may need documentation. It does not provide any specific requirements for pets on domestic flights (such as age minimums, carrier size/type, weight limits) nor specific requirements for service animals on international flights (such as documentation rules, CDC Dog Import Form receipt, microchip proof, vaccination requirements). Therefore it fails to meet the criteria requiring both sets of specific requirements together.
```
</details>

---

##### `tests/stable/test_remediations.py::test_additional_expert_review_1`

**Failures:** 8 times

**Question:** Whats the maximum time we might be stuck on the tarmac without being let off for a domestic flight. Give me exact number of hours and nothing else


<details>
<summary><strong>View full failure log</strong></summary>



```
AssertionError: Failed response: 3 hours

Criteria not met: guardrail should not have been triggered
```
</details>

---

