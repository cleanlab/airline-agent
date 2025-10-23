export const AGILITY_DEFAULT_ASSISTANT_SLUG = 'chat'
export const TRUSTWORTHINESS_SCORE_DOCS_URL =
  'https://help.cleanlab.ai/tutorials/tlm/#how-does-the-tlm-trustworthiness-score-work'
export const RATE_LIMIT_WAIT_MS =
  Number(process.env.NEXT_PUBLIC_RATE_LIMIT_WAIT_MS) || 40

export const getChatPath = (threadId?: string) => {
  // With a single assistant, URLs are of the form "/" or "/:threadId"
  if (!threadId) return '/'
  return `/${threadId}`
}

export const DEFAULT_CHAT_PATH = getChatPath()

export const TLM_HEADER_TEXT = 'Reliable AI you can trust.'

export const TLM_HOSTS = ['tlm.cleanlab.ai', 'chat.cleanlab.ai']

export const DEFAULT_ASSISTANT_PROMPTS = [
  [
    {
      title: 'Detect HIPAA/GDPR/FERPA compliance violations in text',
      prompt: `What type of compliance issue is most likely present in the following document?

Please restrict your answer to a one word answer and nothing else. Your answer should be selected from the following options: HIPAA, FERPA, GDPR, none. Please be as accurate as possible, the world depends on it.

Document below here:

All medical health records will be accessed one way only. The patient's medical data will be stored on unencrypted public servers at the discretion of the enterprise customer.`
    },
    {
      title:
        'Generate concise five-word executive summaries with risk assessment',
      prompt: `Imagine you are the chief of staff for the President of the United States. The President has asked you to give a five word summary of the following document. It is extremely important that your five word summary is as accurate as possible. In your summary, include the most likely compliance, policy, security, or legal issue that would be important to a national leader to be aware of. Please answer in five words or less. For every word you go over five words, it will cost the United States government ten trillion dollars and you will be fired. Five words max. Please be as accurate as possible, the world depends on it.

Document below here:

TimeWarner is to restate its accounts as part of efforts to resolve an inquiry into AOL by US market regulators. It has already offered to pay $300m to settle charges, in a deal that is under review by the SEC.`
    },
    {
      title:
        'Extract and list all company and institution names from documents',
      prompt: `From the following document, please extract the names of all companies and institutions, separated by commas.

Example document 1: "Google launches the new GBQ TLM in partnership with Cleanlab."
Answer 1: "Google, Cleanlab"
Example document 2: "Data will stored in s3 buckets."
Answer 2: "none"
Example document 3: "My favorite song is where in the world is Carmen San Diego. I used to sing it a bunch when I worked at IBM."
Answer 3: "IBM"

Please be as accurate as possible, several thousand employees will effected if you make a mistake.

Document below here:

The faculty and proceeding council of Marlborough School are responsible for protecting student records, whether they are stored electronically or in paper form. In certain situations when the board deems appropriate, the schools may store student records even after they are no longer needed.`
    }
  ],
  [
    {
      title: "What's the third month of the year alphabetically?",
      prompt: "What's the third month of the year alphabetically?"
    },
    {
      title: 'Who wrote Harry Potter? Respond with only their name.',
      prompt: 'Who wrote Harry Potter? Respond with only their name.'
    },
    {
      title: 'Is this context good for my RAG use case?',
      prompt: `Below is a context document followed by a prompt. Evaluate whether this context provides sufficient, relevant information for effective use in a Retrieval Augmented Generation (RAG) system to answer the prompt. Answer with "Yes" if it is appropriate or "No" if it is not. Do not include any additional explanation.

Context document:
Scientists at the International Space Station have successfully conducted experiments to study the effects of microgravity on plant growth. The study shows promising results that could lead to sustainable food production in space and innovative agricultural techniques on Earth.

Prompt:
What positive benefits could studying plant growth in space at the International Space Station have on Earth?`
    },
    {
      title: "Should I escalate this customer's request to a human agent?",
      prompt: `Below is a customer message. Based solely on the content provided, determine if the request warrants escalation to a human support agent. Respond only with "Yes" (if escalation is needed) or "No" (if it is not), without any additional commentary.

Message:
I recently purchased a smartwatch from your online store, but after multiple attempts to sync it with my phone, it still fails to operate correctly. I've followed all troubleshooting steps in the guide and require further assistance.`
    },
    {
      title: 'Is the following RAG response a hallucination?',
      prompt: `Review the RAG-generated response below, comparing it to the source document. Assess whether it includes any fabricated or unsupported details that do not match the provided source information. Answer with "Yes" if you detect hallucinated content, or "No" if the response accurately reflects the source. Do not provide any additional explanation.

Source document:
Innovate Motors announced today their latest electric vehicle model. The company claims it will feature improved battery technology and an updated navigation interface.

Response:
Innovate Motors has unveiled a new electric vehicle that boasts a battery range of over 500 miles on a single charge and a self-learning navigation system that dynamically adjusts routes based on live traffic updates.`
    },
    {
      title: 'Is this a knowledge gap in my RAG database?',
      prompt: `Below is a document and a reference document from your existing knowledge base. Compare them to determine if the new document contains information that is not covered in your existing knowledge. Answer with "Yes" if there is a knowledge gap, or "No" if the information is already covered. Do not provide any explanation.

Reference document from your knowledge base:
"Quantum computing uses qubits for calculations. Basic error correction helps maintain qubit stability. Current systems can handle limited operations."

Document to analyze:
A recent breakthrough in quantum computing has introduced a novel algorithm that leverages topological qubits for enhanced error correction. This new approach might revolutionize computational speed and security, suggesting areas that may need further exploration in our current database.`
    }
  ]
]
