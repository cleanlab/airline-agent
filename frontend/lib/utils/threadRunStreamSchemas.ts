import { z } from 'zod'

const literalSchema = z.union([z.string(), z.number(), z.boolean(), z.null()])
type Literal = z.infer<typeof literalSchema>
type Json = Literal | { [key: string]: Json } | Json[]
const jsonSchema: z.ZodType<Json> = z.lazy(() =>
  z.union([literalSchema, z.array(jsonSchema), z.record(jsonSchema)])
)

const dateSchema = z.string().datetime({ local: true, offset: true })

const usageSchema = z
  .object({
    completion_tokens: z.number().optional(),
    prompt_tokens: z.number().optional(),
    total_tokens: z.number().optional(),
  })
  .passthrough()

const dataSchema = z
  .object({
    id: z.string().uuid().optional(),
    model: z.string().optional(),
    temperature: z.number().optional(),
    instructions: z.string().optional(),
    additional_instructions: z.string().optional(),
    knowledge_base_id: z.string().uuid().optional(),
    weaviate_collection_name: z.string().optional(),
    thread_id: z.string().uuid().optional(),
    assistant_id: z.string().uuid().optional(),
    schema_version: z.number().optional(),
    status: z.enum(['completed', 'in_progress', 'failed']).optional(),
    created_at: dateSchema,
    updated_at: dateSchema,
    usage: usageSchema.optional(),
  })
  .passthrough()

const threadRunFailedSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.run.failed'),
    data: dataSchema.omit({ status: true }).extend({ status: z.literal('failed') }),
  })
  .passthrough()

const threadRunCompletedSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.run.completed'),
    data: dataSchema.omit({ status: true }).extend({ status: z.literal('completed') }),
  })
  .passthrough()

const threadRunUsageSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.run.usage'),
    data: usageSchema,
  })
  .passthrough()

const threadMessageContentDeltaSchema = z.object({
  id: z.string().uuid(),
  object: z.literal('thread.message.content.delta'),
  delta: z
    .object({
      content: z.array(
        z
          .object({
            index: z.number(),
            text_value: z.string().optional(),
          })
          .passthrough()
          .optional()
      ),
    })
    .passthrough(),
})

const scoreSchema = z
  .object({
    score: z.number().optional().or(z.null()),
    is_bad: z.boolean().optional().or(z.null()),
    log: z
      .object({ explanation: z.string().optional().or(z.null()) })
      .passthrough()
      .optional(),
  })
  .passthrough()

const messageMetadataSchema = z
  .object({
    trustworthiness_score: z.number().optional().or(z.null()),
    trustworthiness_explanation: z.string().optional().or(z.null()),
    citations: z.array(z.string()).optional().or(z.null()),
    is_bad_response: z.boolean().optional().or(z.null()),
    is_expert_answer: z.boolean().optional().or(z.null()),

    scores: z
      .object({
        trustworthiness: scoreSchema.optional().or(z.null()),
        response_helpfulness: scoreSchema.optional().or(z.null()),
        context_sufficiency: scoreSchema.optional().or(z.null()),
        response_groundedness: scoreSchema.optional().or(z.null()),
        query_ease: scoreSchema.optional().or(z.null()),
      })
      .passthrough()
      .optional(),
  })
  .passthrough()
  .optional()

const messageSchema = z
  .object({
    thread_id: z.string().uuid(),
    role: z.enum(['user', 'assistant']),
    content: z.string(),
    metadata: messageMetadataSchema,
    schema_version: z.number(),
    id: z.string().uuid(),
    created_at: dateSchema,
    updated_at: dateSchema,
  })
  .passthrough()

const threadMessageCreatedSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.message.created'),
    data: messageSchema,
  })
  .passthrough()

const threadRunInProgressSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.run.in_progress'),
    data: dataSchema.omit({ status: true }).extend({ status: z.literal('in_progress') }),
  })
  .passthrough()

const threadMessageMetadataDeltaSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.message.metadata.delta'),
    delta: z
      .object({
        metadata: messageMetadataSchema,
      })
      .passthrough(),
  })
  .passthrough()

const threadMessageContentCompletedSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.message.content.completed'),
    data: messageSchema,
  })
  .passthrough()

const threadRunStepEventType = z.enum(['message_creation']).or(z.string())
const threadRunStepEventDetails = z
  .object({
    type: z.literal('message_creation'),
    message_creation: z.object({
      message_id: z.string().uuid(),
    }),
  })
  .passthrough()
  .or(
    z
      .object({
        type: z.string(),
      })
      .passthrough()
      .and(jsonSchema)
  )
const threadRunStepEventDataSchema = z
  .object({
    run_id: z.string().uuid(),
    type: threadRunStepEventType,
    step_details: threadRunStepEventDetails,
    status: z.string(),
    schema_version: z.number(),
    id: z.string().uuid(),
    created_at: dateSchema,
    updated_at: dateSchema,
  })
  .passthrough()

const threadRunStepInProgressSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.run_step.in_progress'),
    data: threadRunStepEventDataSchema,
  })
  .passthrough()

const threadRunStepCompletedSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.run_step.completed'),
    data: threadRunStepEventDataSchema,
  })
  .passthrough()

const threadRunStepFailedSchema = z
  .object({
    id: z.string().uuid(),
    object: z.literal('thread.run_step.failed'),
    data: threadRunStepEventDataSchema,
  })
  .passthrough()

type RunStepInProgress = z.infer<typeof threadRunStepInProgressSchema>

type ThreadRunCompleted = z.infer<typeof threadRunCompletedSchema>
type ThreadRunUsage = z.infer<typeof threadRunUsageSchema>
type ThreadMessageContentDelta = z.infer<typeof threadMessageContentDeltaSchema>
type ThreadMessageCreated = z.infer<typeof threadMessageCreatedSchema>
type ThreadMessageContentCompleted = z.infer<typeof threadMessageContentCompletedSchema>
type ThreadRunInProgress = z.infer<typeof threadRunInProgressSchema>
type ThreadRunFailed = z.infer<typeof threadRunFailedSchema>
type ThreadRunStepCompleted = z.infer<typeof threadRunStepCompletedSchema>
type ThreadRunStepFailed = z.infer<typeof threadRunStepFailedSchema>
type ThreadRunStepInProgress = z.infer<typeof threadRunStepInProgressSchema>
type ThreadMessageMetadataDelta = z.infer<typeof threadMessageMetadataDeltaSchema>
type MessageMetadata = z.infer<typeof messageMetadataSchema>

type ThreadStreamChunk =
  | ThreadMessageContentCompleted
  | ThreadMessageContentDelta
  | ThreadMessageCreated
  | ThreadMessageMetadataDelta
  | ThreadRunCompleted
  | ThreadRunFailed
  | ThreadRunInProgress
  | ThreadRunStepCompleted
  | ThreadRunStepFailed
  | ThreadRunStepInProgress
  | ThreadRunUsage

// Add these new type exports
type Usage = z.infer<typeof usageSchema>
type Data = z.infer<typeof dataSchema>
type Message = z.infer<typeof messageSchema>

export {
  dataSchema,
  threadMessageContentCompletedSchema,
  threadMessageContentDeltaSchema,
  threadMessageCreatedSchema,
  threadMessageMetadataDeltaSchema,
  threadRunCompletedSchema,
  threadRunFailedSchema,
  threadRunInProgressSchema,
  threadRunStepCompletedSchema,
  threadRunStepFailedSchema,
  threadRunStepInProgressSchema,
  threadRunUsageSchema,
  usageSchema,
}

export type {
  Data,
  Json,
  Literal,
  Message,
  MessageMetadata,
  RunStepInProgress,
  ThreadMessageContentCompleted,
  ThreadMessageContentDelta,
  ThreadMessageCreated,
  ThreadMessageMetadataDelta,
  ThreadRunCompleted,
  ThreadRunFailed,
  ThreadRunInProgress,
  ThreadRunStepCompleted,
  ThreadRunStepFailed,
  ThreadRunUsage,
  ThreadStreamChunk,
  Usage,
}
