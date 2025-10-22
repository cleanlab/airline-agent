'use client'

import { Collapsible } from 'radix-ui'
import type { ReactNode } from 'react'

import { IconCheckCircleFilled, IconChevronDown, IconInfo } from '../icons'
import { cn } from '@/lib/utils/tailwindUtils'
import type {
  EvalResult,
  MessageMetadataOutput,
  ResponseScoreMetadataOutput
} from './MessageAssistant'

const DEFAULT_TRUSTWORTHINESS_EXPLANATION =
  'Did not find a reason to doubt trustworthiness.'
const DEFAULT_HELPFULNESS_EXPLANATION =
  'Evaluates whether the response effectively addresses the user query and appears helpful.'
const DEFAULT_INSUFFICIENT_CONTEXT_EXPLANATION =
  'Evaluates whether the retrieved context contains sufficient information to completely answer the query. A low score indicates that key information is missing from the context (perhaps due to poor retrieval or missing documents).'
const DEFAULT_RESPONSE_GROUNDEDNESS_EXPLANATION =
  'Evaluates whether claims/information stated in the response are explicitly supported by the provided context.'
const DEFAULT_QUERY_EASE_EXPLANATION =
  'Evaluates whether the user query seems easy for an AI system to properly handle. Complex, vague, tricky, or disgruntled-sounding queries receive lower scores.'

type ScoreType = keyof ResponseScoreMetadataOutput

interface Issue {
  type: ScoreType
  text: string
  score?: number
  explanation?: string
}

const explanationDict: Record<ScoreType, string> = {
  trustworthiness: DEFAULT_TRUSTWORTHINESS_EXPLANATION,
  response_helpfulness: DEFAULT_HELPFULNESS_EXPLANATION,
  context_sufficiency: DEFAULT_INSUFFICIENT_CONTEXT_EXPLANATION,
  response_groundedness: DEFAULT_RESPONSE_GROUNDEDNESS_EXPLANATION,
  query_ease: DEFAULT_QUERY_EASE_EXPLANATION
}

const issueTextDict: Record<ScoreType, string> = {
  trustworthiness: 'Untrustworthy',
  response_helpfulness: 'Unhelpful',
  context_sufficiency: 'Insufficient Context',
  response_groundedness: 'Ungrounded',
  query_ease: 'Poor Query'
}

const issuePriority: Record<ScoreType, number> = {
  response_helpfulness: 1,
  response_groundedness: 2,
  context_sufficiency: 3,
  trustworthiness: 4,
  query_ease: 5
}

function getTopIssue(scores?: ResponseScoreMetadataOutput): Issue | undefined {
  if (!scores) return undefined

  const issues: Issue[] = []

  // First check for trustworthiness issues
  if (scores.trustworthiness?.triggered) {
    issues.push({
      type: 'trustworthiness',
      text: issueTextDict.trustworthiness,
      score: scores.trustworthiness.score ?? undefined,
      explanation: scores.trustworthiness.log?.explanation ?? ''
    })
  }

  // Then add all other issues
  Object.entries(scores).forEach(([key, value]) => {
    const scoreType = key as ScoreType
    const result = value as EvalResult

    if (scoreType !== 'trustworthiness' && result?.triggered) {
      issues.push({
        type: scoreType,
        text: issueTextDict[scoreType],
        score: result.score ?? undefined,
        explanation: result.log?.explanation ?? explanationDict[scoreType]
      })
    }
  })

  if (issues.length === 0) return undefined

  return issues.sort((a, b) => issuePriority[a.type] - issuePriority[b.type])[0]
}

const IssueDescription = ({
  iconStart,
  title,
  description,
  score,
  scoreTitle
}: {
  iconStart?: ReactNode
  title: string
  description: string
  score?: number
  scoreTitle: string
}) => {
  return (
    <div
      className={cn(
        'type-body-200 flex flex-col gap-2 text-text-faint',
        !description && 'gap-0'
      )}
    >
      <div className="flex items-center gap-5">
        {iconStart}
        <p className="type-body-200-semibold text-text-primary">{title}</p>
      </div>
      {description && <p>{description}</p>}
      {score !== undefined && (
        <p>
          {scoreTitle}: {score.toFixed(3)}
        </p>
      )}
    </div>
  )
}

interface IssuesAccordionProps {
  messageMetadata: MessageMetadataOutput
}

function IssuesAccordion({ messageMetadata }: IssuesAccordionProps) {
  const { is_expert_answer: isExpertAnswer, scores } = messageMetadata
  const topIssue = isExpertAnswer ? undefined : getTopIssue(scores ?? {})
  const issuesText = topIssue?.text ?? topIssue?.type ?? ''
  const hasIssues = !!topIssue
  const showIssues = hasIssues
  const evaluations = (
    Object.keys(scores ?? {}) as (keyof ResponseScoreMetadataOutput)[]
  ).filter(evaluation => evaluation !== topIssue?.type)

  return (
    <Collapsible.Root className="w-full rounded-3 border border-border-1 bg-surface-1">
      <Collapsible.Trigger
        disabled={!!isExpertAnswer}
        className="group type-body-200 flex w-full items-center justify-between gap-5 rounded-3 p-5 text-text-primary outline-none -outline-offset-1 transition-colors focus-visible:outline-1 focus-visible:ring-2 focus-visible:ring-focus"
      >
        <div className="flex items-start gap-5">
          {showIssues ? (
            <IconInfo size={20} className="pt-px text-red-400" />
          ) : (
            <IconCheckCircleFilled size={20} className="pt-px text-green-400" />
          )}
          <div className="flex text-start">
            {showIssues
              ? `Issue detected: ${issuesText}`
              : 'No issues detected'}
          </div>
        </div>
        {!isExpertAnswer && (
          <IconChevronDown
            className="text-text-faint transition-transform duration-200 group-data-[state=open]:rotate-180"
            size={20}
          />
        )}
      </Collapsible.Trigger>
      <Collapsible.Content className="overflow-hidden data-[state=closed]:animate-collapsible-close data-[state=open]:animate-collapsible-open">
        <div className="flex flex-col gap-5 p-5 pt-0 text-text-primary">
          {/* Display single issue if it exists */}
          {topIssue && (
            <IssueDescription
              title={issueTextDict[topIssue.type]}
              description={
                topIssue.explanation ?? explanationDict[topIssue.type]
              }
              score={topIssue.score}
              scoreTitle={
                topIssue.type === 'trustworthiness'
                  ? 'Trustworthiness Score'
                  : `${topIssue.type}`
              }
            />
          )}

          {/* If no issues, show the trustworthiness status */}
          {!hasIssues && scores?.trustworthiness && (
            <>
              {showIssues && <hr className="border-border-1" />}
              <IssueDescription
                iconStart={
                  showIssues && (
                    <IconCheckCircleFilled
                      size={20}
                      className="text-green-400"
                    />
                  )
                }
                title="Trustworthy"
                description={
                  scores.trustworthiness.log?.explanation ??
                  DEFAULT_TRUSTWORTHINESS_EXPLANATION
                }
                score={scores.trustworthiness.score ?? undefined}
                scoreTitle="Trustworthiness Score"
              />
            </>
          )}

          {scores && (
            <Collapsible.Root>
              <Collapsible.Trigger className="group type-body-200 flex w-full items-center justify-between gap-5 rounded-1 text-text-primary outline-none -outline-offset-1 transition-colors focus-visible:outline-1 focus-visible:ring-2 focus-visible:ring-focus">
                <p>More evaluations</p>
                <IconChevronDown
                  className="text-text-faint transition-transform duration-200 group-data-[state=open]:rotate-180"
                  size={20}
                />
              </Collapsible.Trigger>
              <Collapsible.Content className="overflow-hidden data-[state=closed]:animate-collapsible-close data-[state=open]:animate-collapsible-open">
                <div className="flex flex-col gap-3 pt-3">
                  {evaluations.map(evaluation => (
                    <IssueDescription
                      key={evaluation}
                      title=""
                      description=""
                      score={scores[evaluation]?.score ?? undefined}
                      scoreTitle={evaluation as string}
                    />
                  ))}
                </div>
              </Collapsible.Content>
            </Collapsible.Root>
          )}
          <Collapsible.Root>
            <Collapsible.Trigger className="group type-body-200 flex w-full items-center justify-between gap-5 text-text-primary">
              <p>How does this work?</p>
              <IconChevronDown
                className="text-text-faint transition-transform duration-200 group-data-[state=open]:rotate-180"
                size={20}
              />
            </Collapsible.Trigger>
            <Collapsible.Content className="overflow-hidden data-[state=closed]:animate-collapsible-close data-[state=open]:animate-collapsible-open">
              <p className="type-body-200 pt-3 text-text-faint">
                Cleanlab uses a state-of-the-art LLM uncertainty estimation to
                detect in real time (&lt;1s) whether your agent/LLM answer is
                correct for the given query, or satisfying other evaluation
                criteria. The scores are computed by combining proprietary
                methods in epistemic uncertainty and aleatoric uncertainty
                estimation with the best versions of common approaches like
                LLM-as-a-judge, probabilistic, and consistency estimation.
                Evaluation scores are peer-reviewed and benchmarked as the most
                accurate real-time response accuracy and trust scores, while
                minimizing cost and latency for production AI and agentic RAG
                systems.
              </p>
            </Collapsible.Content>
          </Collapsible.Root>
        </div>
      </Collapsible.Content>
    </Collapsible.Root>
  )
}

export { IssuesAccordion }
