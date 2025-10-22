'use client'

import type { HTMLAttributes, ReactNode } from 'react'
import type { ValueOf } from 'type-fest'

import { Badge } from './Badge'
import { CleanlabLogo } from './CleanlabLogo'
import { cn } from '@/lib/utils/tailwindUtils'
import { IssuesAccordion } from './IssuesAccordion'
import { MessageMarkdown } from './MessageMarkdown'

type EvalLog = {
  explanation?: string | null
}

type EvalResult = {
  score?: number | null
  triggered?: boolean | null
  triggered_escalation?: boolean | null
  triggered_guardrail?: boolean | null
  log?: EvalLog | null
}

type ResponseScoreMetadataOutput = {
  [key: string]: EvalResult | null | undefined
}

type MessageMetadataOutput = {
  trustworthiness_score?: number | null
  trustworthiness_explanation?: string | null
  is_expert_answer?: boolean | null
  guardrailed?: boolean | null
  escalated_to_sme?: boolean | null
  citations?: string[] | null
  scores?: ResponseScoreMetadataOutput | null
}

const WaitingDot = ({ className }: { className?: string }) => {
  return (
    <div
      className={cn(
        'size-3 shrink-0 grow-0 animate-[cleanlab-dot-bounce_1s_infinite] rounded-full bg-text-disabled',
        className
      )}
    />
  )
}

const WaitingAnimation = () => {
  return (
    <div
      className="flex w-fit shrink-0 grow-0 gap-2 overflow-hidden rounded-full border border-border-1 bg-surface-1 p-4"
      aria-label="Waiting for response"
    >
      <WaitingDot className="[animation-delay:-0.3s]" />
      <WaitingDot className="[animation-delay:-0.15s]" />
      <WaitingDot />
    </div>
  )
}

const Status = {
  ContentPending: 'contentPending',
  MetadataPending: 'metadataPending',
  Done: 'done'
} as const
type MessageAssistantStatusT = ValueOf<typeof Status>

const AssistantIcon = ({
  icon,
  isLoading,
  className
}: {
  icon: ReactNode
  isLoading?: boolean | undefined | null
  className?: string
}) => {
  return (
    <div
      className={cn(
        'relative flex size-9 shrink-0 grow-0 select-none items-center justify-center overflow-hidden rounded-2 bg-surface-0 p-1 shadow-elev-0 outline outline-1 -outline-offset-1 outline-border-1',
        className
      )}
    >
      <div
        className={cn(
          'absolute left-[-22%] top-[-22%] flex size-[142%] origin-center animate-spin items-center justify-center bg-gradient-to-l from-neutral-900/15 to-transparent opacity-0 transition-opacity duration-500 [animation-duration:2.5s]',
          isLoading && 'opacity-100'
        )}
      />
      {/* Relative position assures logo appears above loading background */}
      <div className="relative">{icon ?? <CleanlabLogo size={21} />}</div>
    </div>
  )
}

function MessageAssistant({
  content,
  className,
  icon,
  messageMetadata,
  status = Status.Done,
  feedback,
  error,
  allowHtml = false,
  tlmError: tlmErrorProp,
  showAccordion = false,
  disableScores = false,
  ...props
}: {
  content: string
  messageMetadata: MessageMetadataOutput | null
  className?: string
  status: MessageAssistantStatusT
  error?: string | undefined
  allowHtml?: boolean
  tlmError?: string | undefined
  icon?: ReactNode | undefined
  feedback?: ReactNode | undefined
  showAccordion?: boolean
  disableScores?: boolean
} & HTMLAttributes<HTMLDivElement>) {
  let contentNode: ReactNode

  const {
    trustworthiness_score: trustworthinessScore,
    trustworthiness_explanation: trustworthinessExplanation,
    citations
  } = messageMetadata ?? {}

  const tlmScoreValid =
    typeof trustworthinessScore === 'number' &&
    Number.isFinite(trustworthinessScore)
  const tlmLoading = !tlmScoreValid && status === Status.MetadataPending
  const tlmError =
    tlmErrorProp || (status === Status.Done && !tlmScoreValid && 'N/A')
  const showMessageScores =
    !disableScores && (tlmError || tlmScoreValid || tlmLoading)

  if (!content) {
    if (status !== Status.Done) {
      contentNode = <WaitingAnimation />
    } else {
      contentNode = (
        <Badge size="large" className="w-fit grow-0">
          No response
        </Badge>
      )
    }
  } else {
    contentNode = (
      <>
        <MessageMarkdown allowHtml={allowHtml}>{content}</MessageMarkdown>
        {showMessageScores && (
          <div className="flex justify-between gap-4 pt-5">
            <div
              className={cn(
                'flex flex-wrap gap-x-5 gap-y-2',
                showAccordion && 'w-full'
              )}
            >
              {showAccordion && (
                <IssuesAccordion messageMetadata={messageMetadata ?? {}} />
              )}
            </div>
            {!showAccordion &&
              Number.isFinite(trustworthinessScore) &&
              !error &&
              feedback}
          </div>
        )}
        {error && <p className="text-foreground">Error: {error}</p>}
      </>
    )
  }

  return (
    <div
      className={cn('group relative flex items-start gap-4', className)}
      {...props}
    >
      <AssistantIcon icon={icon} isLoading={status !== Status.Done} />
      <div
        // Using negative margin that matches padding makes sure focus-rings are
        // visible outside of the overflow-hidden container
        className={cn(
          '-m-1 flex flex-1 flex-col space-y-2 overflow-hidden p-1',
          !content && 'justify-center self-stretch'
        )}
      >
        {contentNode}
      </div>
    </div>
  )
}

export {
  AssistantIcon,
  type EvalResult,
  MessageAssistant,
  Status as MessageAssistantStatus,
  type MessageAssistantStatusT,
  type MessageMetadataOutput,
  type ResponseScoreMetadataOutput
}
