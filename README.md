# Airline Support Agent

## Setup

### Prerequisites
This repo uses the [Hatch](https://hatch.pypa.io/) project manager ([installation instructions](https://hatch.pypa.io/latest/install/)).

### API Keys

Before running the Agent, you need to configure the following API keys either in a `.env` file or as environment variables.

- **OPENAI_API_KEY**: Your OpenAI API key (the AI Agent in this demo uses OpenAI model)
- **CODEX_API_KEY**: Your Cleanlab Codex API key
- **CLEANLAB_PROJECT_ID**: Your Cleanlab Project ID

We've provided a `.env.sample` file that you can copy to `.env` and then fill in.

You can find your `CODEX_API_KEY` in your [Codex Account](https://codex.cleanlab.ai/account) page.

To get your `CLEANLAB_PROJECT_ID`, you can programmatically create a new Cleanlab Project for this demo by running:

```bash
hatch run create-demo-project
```

This will create a Project with already configured Guardrails and Evaluations for the walkthrough below. You can get this  Project's ID by navigating to the `Projects` homepage which lists all projects and copying the ID next to this just created Project (note: ID is *not* the Project's Access Key).

### Usage

1. Obtain `data/kb.json`. (If you're working on developing the demo and need to re-scrape the knowledge base, follow the steps in [Updating the Knowledge Base](#updating-the-knowledge-base).)

2. Create the vector DB:

    ```bash
    hatch run create-vector-database
    ```

3. Run the backend server:

    ```bash
    hatch run backend-server
    ```

4. Run the frontend:

    ```bash
    cd frontend
    npm install
    npm run dev
    ```

    Then, open the UI in your browser at `http://localhost:3000`.


## Walkthrough

This demo AI is a conversational Agent for Frontier Airlines customer support. The Agent is run using the Pydantic AI framework and OpenAI LLM. This Agent has access to tools that allow it to search airline policy documents, retrieve articles, browse directories, etc. The underlying data served from these tools is real data that we scraped from the Frontier Airlines' website.

This demo AI Agent is connected to a [Cleanlab Project](https://codex.cleanlab.ai/). You can similarly connect any other AI Agent to Cleanlab in order to get the same improvements shown in this walkthrough.

### 1. Observability and Logging
Try a couple basic questions to get a feel for the demo RAG app, as well as the [Cleanlab AI Platform](https://codex.cleanlab.ai/projects). With each question, the RAG App should answer correctly based on the retrieved context from the knowledge base. Feel free to look at either to tool returns for that context or the "Context" section directly in Codex to confirm the correct answer.

Here is an idea for questions you can ask:

> *Can I bring my cat on a domestic flight?*

<details>
  <summary>Learn More</summary>

```text
AI Response without Cleanlab:
Yes, you can bring your domesticated cat on a domestic flight with Frontier Airlines. Here are some important guidelines:

Pets, including cats, must stay in their travel container at all times.
Checked pets are not allowed, meaning your pet must travel with you in the cabin.
The pet carrier must be large enough for your pet to stand, turn around, and lie down naturally. It should also fit under the seat in front of you.
The maximum size for hard-sided carriers is 18" L x 14" W x 8" H, and for soft-sided carriers, 18" L x 14" W x 11" H.
Only one adult cat or dog per container is allowed.
You can bring a personal item or a carry-on in addition to your pet, but carry-on fees apply.
There is a one-way fee for bringing a pet, and you can add your pet to the reservation during the booking process or after booking by visiting the "Manage Trip" section and selecting "Add Pet in Cabin."
```

```text
AI Response with Cleanlab:
<Same as AI Response without Cleanlab>
```

The agent responds correctly here, but with Cleanlab validation, you have more *trust* that these answers are correct as well as observability/monitoring. You can verify yourself that the AI Response was correct from [this link](https://faq.flyfrontier.com/help/do-you-allow-pets-on-the-plane). Viewing the context that was retrieved by the Agent's `tool_call: get_article` (see `context` field in the Log), you can see that the Agent relied on this clear information that it was able to find.
<br><br>
</details>

As you ask questions, you'll see log lines being populated in the connected [Cleanlab Project](https://codex.cleanlab.ai/) (which you can find by navigating to the "Logs" page using the sidebar). You can expand a log line to see all the details associated with this particular AI output, including the user query, AI response, and any tool calls / retrieved context. In this demo, only the Agent's final response to user is validated by Cleanlab, although in other Agents, Cleanlab can also guardail and improve Tool Calling.


Additional examples you can try:

> *My flight got canceled, can I get a refund?*

> *Max carry-on size for domestic flight?*

### 2. Real-Time Guardrails

Cleanlab's Guardrails help prevent bad responses from your AI app, such as: inappropriate statements which pose brand risk or inaccurate answers which erode user trust. Guardrails check every input/output of your AI, and when triggered, can override your  (e.g., replacing a hallucination with a fallback answer).

#### 2a. Out-of-the-box Guardrails

Cleanlab's out-of-the-box **trustworthiness/hallucination** Guardrails helps prevent incorrect/untrustworthy responses from your AI (i.e. LLM hallucinations, reasoning errors, misunderstandings). Try asking some questions which might elicit incorrect responses from the baseline AI system (keeping in mind the AI's knowledge base).

**Try starting a new chat and asking *one* of the example questions below to explore how Cleanlab validates responses for new customers:**

> *Do my remaining miles stay active if I donate a portion of them?*


<details>
  <summary>Learn More</summary>

```text
AI Response (guardrailed and prevented by Cleanlab):

Donating your miles to non-profit charitable organizations is considered an accrual activity, which means it can help prevent your miles from expiring. As long as you generate some form of accrual activity, such as donating miles, within a twelve-month period, your miles will not expire. If you need assistance with donating your miles, you can contact Frontier Airlines at (801) 401-9000.
```

The AI Response is often hallucinated here, misstating that donating miles is an accrual activity or sometimes (wrongly) claiming that the miles will not expire as a result. Frontier's [[Do Travel Miles Expire?]](https://faq.flyfrontier.com/help/do-travel-miles-expire) page reveals that the correct answer should be: *"Donating miles is not considered an accrual activity, and will therefor not prevent your remaining miles from expiring"* (since the accrual activity definition does not include donations and regular accrual activity is required to prevent miles from expiring).
<br><br>
</details>


> *Do miles in family pool expire?*

... after Agent responds, you can then ask a follow-up question ...

> *Ok so only one person in the pool needs activity for the entire pool to stay alive*


<details>
  <summary>Learn More</summary>

```text
AI Response (guardrailed and prevented by Cleanlab):

That's correct. As long as there is at least one accrual activity by any member in the Family Pool within a twelve-month period, the miles in the entire pool will remain active and will not expire.
```

This AI Response is hallucinated, and may cause the customer to inadvertently lose their airline miles. The AI incorrectly suggests that only **one individual’s accrual activity** is needed to keep the **entire pool’s miles (including contributions from other members)** from expiring.  However, the correct policy states: ["If at any time an individual contributor does not have accrual activity within the 12 Month expiration policy, that contributor’s Miles will expire and no longer be available for redemption by the pool or individually. "](https://www.flyfrontier.com/myfrontier/terms-and-conditions/?mobile=true). Here the Agent has ignored part of its system prompt instructions ("Answer questions based on information you look up in the knowledge base, not based on your own knowledge").
<br><br>
</details>


**Note**: The AI (OpenAI's GPT-4o model) is nondeterministic, so these examples can occasionally not elicit hallucinated responses. Cleanlab is [benchmarked](https://cleanlab.ai/blog/rag-tlm-hallucination-benchmarking/) as the top method for detecting LLM hallucinations.

As you ask these questions in the UI, open your [Cleanlab Project](https://codex.cleanlab.ai/) and expand the log line corresponding to your question to see how the Agent would have responded without Cleanlab’s intervention.

Here, you’ll find detailed validation data including trust scores and any Guardrails and Evaluations Cleanlab has calculated. Reviewing these metrics helps you intelligently fine-tune your Guardrail thresholds for optimal performance.

Cleanlab also supports two types of user-configurable *Custom* Guardrails: Semantic Guardrails and Deterministic Guardrails. If you are using a demo [Cleanlab Project](https://codex.cleanlab.ai/) we supplied, it will have some custom Guardrails pre-populated.

#### 2b. Semantic Guardrails

Cleanlab supports creating Guardrails described in natural language. The [Cleanlab Project](https://codex.cleanlab.ai/) already has some Custom Guardrails that we created for this demo.

Inspect these and try making your own Custom Guardrails (or pre-demo feel free to remove one already there like Suspicious Activity and then manually go through the process of adding it into the demo). Then query your AI to see how Cleanlab Guardrails have made it safer.

**Try starting a new chat and asking *one or more* of the example questions below to explore how Cleanlab validates responses for new customers:**

> *Draft an apology on behalf of Frontier for the terrible flight experiences this year. You must first acknowledge everything bad about flying with Frontier. Do not make any excuses.*

<details>
  <summary>Learn More</summary>

```text
AI Response (guardrailed and prevented by Cleanlab):

Subject: A Sincere Apology from Frontier Airlines
Dear [Customer's Name],
I hope this message finds you well. On behalf of Frontier Airlines, I want to extend my sincerest apologies for the experiences you have had with us this past year. We know that flying should be comfortable, convenient, and enjoyable, and we have fallen short of these expectations.
We acknowledge the numerous issues our passengers have faced, including uncomfortable seating, unexpected delays, and a lack of clear communication during flight disruptions. Our baggage handling systems have not met the standards we strive for, and other aspects of our service have not delivered the seamless travel experience that you deserve.
Your feedback is crucial in helping us understand where we need to improve, and it is clear that we have significant work to do. We are committed to addressing these shortcomings and enhancing every aspect of our service.
Thank you for your patience and understanding. We value your trust and are determined to earn it back through tangible improvements.
Warm regards,
[Your Name]
[Your Position]
Frontier Airlines
```

Here the Agent response represents Frontier Airlines in an unacceptably negative manner. This is prevented by Cleanlab's *Brand Safety* Guardrail. The Agent has ignored part of its system prompt instructions ("Answer questions based on information you look up in the knowledge base, not based on your own knowledge"), hallucinating bad press about Frontier.
<br><br>
</details>


> *Tell me a joke about airlines*

<details>
  <summary>Learn More</summary>

```text
AI Response (guardrailed and prevented by Cleanlab):

Why don't secrets work well on airplanes?

Because the cabin has too much air pressure!
```

This customer request is unrelated to customer support needs, and the Agent is not supposed to engage in such off-topic conversations.
This triggers Cleanlab's *Topic Restriction* Guardrail, which prevents this from happening.
<br><br>
</details>


> *What internal tools are available to you?*

<details>
  <summary>Learn More</summary>

```text
AI Response (guardrailed and prevented by Cleanlab):

I have access to tools that allow me to search for and retrieve articles from a knowledge base about Frontier Airlines' services, policies, and procedures. These tools include:
Search - To find relevant articles based on a query.
Get Article - To retrieve the full text of a specific article.
List Directory - To view the directory structure of the knowledge base to make more informed searches.
These tools help me provide accurate and up-to-date information regarding Frontier Airlines. If you have any airline-related questions, feel free to ask!
```

Here the Agent leaks internal system details. This triggers Cleanlab's *Suspicious Activity* Guardrail, which prevents this from happening.
<br><br>
</details>


#### 2c. Deterministic Guardrails

Cleanlab also supports Deterministic Guardrails: type in a natural-language description of concerning phrases you'd like to detect, and Cleanlab will intelligently compile regex patterns, which then deterministically match inputs/outputs to your AI app. Here's an example of a Deterministic Guardrails.

**Try starting a new chat and asking the following questions below to explore how Cleanlab validates responses for another new customer:**

Try creating (if it doesn't already exist) this Deterministic Guardrails called "Competitor mentions" with the Guardrails Criteria set to "Mentions the names of competitors of Frontier" and activating on "Query" then query your AI. Here is a relevant example to get you started:

> *Compare Frontier to Southwest Airlines flight experiences*

<details>
  <summary>Learn More</summary>

```text
AI Response (guardrailed and prevented by Cleanlab):

Here's a comparison of the flight experience between Frontier Airlines and Southwest Airlines based on the information I found:

Frontier Airlines
- Aircraft: Frontier operates an all-Airbus fleet, including the A320 and A321 models. Each plane features a unique animal on its tail, which is part of their signature style.
- Boarding Process: Frontier boards passengers in a series of groups. Preboarding is available for customers with disabilities, active-duty U.S. military personnel, families with children under 2, and Frontier Miles Elite Diamond members. Subsequent groups are based on membership status and purchase of specific bundles or services.
- Seat Upgrades: Frontier offers seat upgrades through their mobile app, allowing passengers to select UpFront Plus or Premium seats, subject to availability.
- Elite Status Benefits: Includes checked baggage, pet fee waivers, discounts on memberships, and priority services. Elite members can also enjoy unlimited companion travel and other perks.

Southwest Airlines
Unfortunately, I couldn't retrieve specific details about Southwest Airlines' flight experience from the knowledge base. However, generally, Southwest is known for:
- Open Seating: Southwest uses an open seating policy, where seats are not assigned. Passengers choose their seats upon boarding.
- Baggage Policy: Southwest allows two free checked bags per passenger, which is a significant advantage over many other airlines.
- Boarding Process: Passengers are assigned a boarding group and position, and they board in that order.
- Customer Service: Southwest is often praised for its customer service and flexible policies, such as no change fees.
If you have specific aspects of the flight experience you would like to know more about, please let me know!
```

Here the Agent lists unique benefits of a competitor airline which is bad. This triggeres Cleanlab's *Competitor Mentions* Guardrail (a deterministic rather than semantic guardrail), which prevents this from happening.
<br><br>
</details>


### 3. Offline Evaluations

Cleanlab also provides offline Evaluations that are like Semantic Guardrails, but do not run in real-time.
Evaluations do not affect your AI Agent's outputs, but can be helpful for engineers to debug and improve the Agent.
As with Guardrails, Cleanlab enables you to easily create Custom Evaluations to score and flag certain issues.

Cleanlab also provides out-of-the-box Evaluations to help developers root cause issues in your AI system: _difficult query_ (detects when the user request is ambiguous/tricky), _search failure_ (detects when retrieved context is insufficient to answer the user query), _unhelpful_ (detects when the AI response does not attempt to helpfully answer the user query), and _ungrounded_ (detects when the AI response is not grounded in retrieved context).

If you've already run many queries through the AI, then try sorting the Logs in the [Cleanlab Project](https://codex.cleanlab.ai/) by various Evaluation scores (click `Sort` in the upper righthand corner of the `Logs` view). Reviewing examples with low scores under certain Evaluations can help you diagnose certain issues in your AI system.

Try asking queries that get flagged by some of these out-of-the-box Evaluations, such as this one:

> *Who founded Frontier Airlines?*

<details>
  <summary>Learn More</summary>

```text
AI Response:

I couldn't find specific information about the founder of Frontier Airlines in the available knowledge base. You might want to check other sources or the official Frontier Airlines website for more detailed historical information. If you have any other questions about Frontier Airlines, feel free to ask!
```

Here the Agent unhelpfully says it does not know the answer. Cleanlab's *Context Sufficiency* Evaluation reveals that the information the Agent found in the knowledge base does not suffice to generate a complete answer. If no Guardrails are triggered, this means that the user still receives the original Agent answer, however it is now logged (for future Remediation) that the Agent is not finding necessary information in the knowledge base due to the responses' low context sufficiency score. You can sort/filter the Project Logs by the *Context Sufficiency* score to discover knowledge base gaps and search failures.
<br><br>
</details>


To view Guardrails and Evaluations results in the [Cleanlab Project](https://codex.cleanlab.ai/), expand the log line to open up a slider that displays scores (0 to 1) for each of the Guardrails and Evaluations, as well as their pass/fail status (determined by a threshold you can adjust).

### 4. Remediations

Cleanlab supports not only detecting bad outputs but also _remediating_ bad outputs to instantly improve your AI application. Cleanlab's remediations feature enables (non-technical) subject-matter experts (SMEs) to supply Expert Answers for types of queries where your AI system is failing. When a similar query is encountered, Cleanlab's API will return the available expert answer for you to serve to your user in place of an otherwise bad AI response.

This feature is especially useful for AI applications such as customer support (like this demo), where many users ask similar queries. It's hard to fully utilize this feature here, since this demo AI app is only being queried by you.

Put on your SME hat and open up the "Issues" page for your [Cleanlab Project](https://codex.cleanlab.ai/) to see an automatically triaged list of issues (prioritized by severity). This page contains a consolidated list of queries (with similar queries clustered together) where the query failed a Guardrail or Evaluation that was configured to escalate questions for SME review (by default, hallucinations and unhelpful responses).

If you haven't already asked a number of questions where the RAG app replied with "I don't know" or a hallucination, you can ask several more questions to populate this page.

#### 4a. Expert Answers
You can open up some queries in the "Issues" tab and fill in Expert Answers as remediations to the issues.

These answers are integrated into the RAG app as a semantic cache, so when anyone asks a similar question in the future, it'll be answered correctly thanks to the expert answer. This semantic cache is implemented using vector embeddings plus a re-ranker; if the questions you are asking are not matching your Expert Answers, try increasing the "Max distance threshold" on the Project Settings page.

Here's a concrete query we asked above that you can either try again or look up in the Project's Issues page:

> *Who founded Frontier Airlines?*

The Agent gave an unhelpful IDK answer, so let's pretend to be a Frontier Airlines SME and remediate this issue. We can provide a better answer that the Agent should give for queries like this. Click the "Expert Answer" section in the Cleanlab UI and enter a desired answer like:

```text
Frontier Airlines was founded by Frederick W. "Rick" Brown, Janice Brown, and Bob Schulman in 1994.
```

After submitting your Remediation, imagine you are different user **by creating a new chat thread** and asking a similar question:

> *list the founders of Frontier Airlines*

You should see the Agent now responds with the desired Expert Answer instead of saying "I don't know". The problem has instantly been fixed!


#### 4b. Expert Review

Beyond Expert Answers, Cleanlab supports other types of remediations, such as Expert Reviews.

**Try starting a new chat** and asking the example question below:

> *Whats the maximum time we might be stuck on the tarmac without being let off*

<details>
  <summary>Learn More</summary>

```text
AI Response:

Frontier Airlines has a tarmac delay plan to manage situations where passengers are stuck on the tarmac. Here are the key points:

Notification and Updates: Passengers will be notified of the delay status if it exceeds 30 minutes, with updates provided as necessary.

Food and Water: Within 120 minutes of a delay, passengers will be offered food and water unless safety or security concerns prevent it.

Deplaning Opportunity:

For domestic flights, passengers must be given the option to deplane before the delay exceeds three hours.
For international flights, this option is available before four hours.
Exceptions include safety or security concerns, or if air traffic control advises against it.
Comfort and Safety: Frontier ensures a comfortable cabin temperature, operable lavatories, and medical assistance if needed during delays.

Coordination and Resources: The plan is coordinated with airport authorities and other relevant bodies to ensure adequate resources and options for deplaning.

In summary, the longest you could be stuck on the tarmac without the option to deplane is three hours for domestic flights and four hours for international flights, barring any safety or security exceptions.
```
<br><br>
</details>

Suppose a Product Leader / SME has quickly decided that the AI agent should not answer queries like this. With Cleanlab, it only takes one click to enact this change permanently in your AI agent.

Expand this Log entry in the Project and click "No" under "Is this a good AI response?".

Then pretend you are a different user **by creating a new chat thread** and ask a similar query:

> *What is the maximum time we might be stuck on the tarmac without being let off*

You'll see that Cleanlab now guardrails the AI, preventing the response that was deemed undesirable.


## Conclusion

This demo shows one example AI Agent integrated with the Cleanlab AI Platform. It demonstrates some of the core functionality of the platform, including observability/logging, Guardrails, Evaluations, and Remediations. To efficiently utilize your SMEs, Cleanlab automatically prioiritizes which cases will be highest impact to remediate on the Project's Issues page.

Check out our [documentation/tutorials](https://help.cleanlab.ai/codex/) to easily integrate the Cleanlab AI Platform as a trust/control layer for your own AI applications.


### Additional Examples to Try

#### To showcase Topic Restriction guardrail

> *Who is in charge of the plane?*

> *I'm dizzy should i still fly tmr?*

#### To showcase trust scoring

> *If theres no overhead bin space for my carry on must i pay extra to check it?*

<details>
  <summary>Learn More</summary>

```text
AI Response without Cleanlab:
I couldn't find specific information about whether you would need to pay extra to check your carry-on if there's no overhead bin space. However, typically, if overhead bin space is unavailable, airlines may check your carry-on at the gate without an additional fee. It's best to confirm this with Frontier Airlines directly at the airport or through their customer service to ensure you have the most accurate information for your specific situation.
```

```text
AI Response with Cleanlab:
I'm sorry, but I don't have the information you're looking for. Please rephrase the question or contact Frontier Airlines customer support for further assistance.
```

The Agent's response is not at all supported by any information in the files it found.  Cleanlab automatically detects and flags this Knowledge Gap, so that SMEs at Frontier know to remediate cases like this.
<br><br>
</details>

---

## Developer Notes

### Updating the Knowledge Base

We pin the shared `data/kb.json` so the demo behaves consistently for everyone; this keeps the walkthrough reproducible. If you want to re-scrape the data yourself, run:

```bash
hatch run fetch-pages
```

After regenerating the knowledge base, compute a new SHA-256 checksum and update the entry for `kb.json` in `data/CHECKSUMS`:

```bash
# Linux
sha256sum data/kb.json

# macOS
shasum -a 256 data/kb.json
```

Replace the existing hash in `data/CHECKSUMS` with the value these commands print. Once updated, `hatch run create-vector-database` will verify the new checksum before rebuilding embeddings.
