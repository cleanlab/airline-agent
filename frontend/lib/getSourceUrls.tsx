type SourceListSourcesRouteResponse = Array<{
  source_params: {
    name: string
    urls?: string[]
    bucket_name?: string
  }
}>

export function getSourceUrls(
  sources: SourceListSourcesRouteResponse | null | undefined
) {
  return sources?.flatMap(source => {
    if (source.source_params.name === 'web_v0') {
      return source.source_params?.urls
    }
    if (source.source_params.name === 'notion_v0') {
      return [`Notion: ${source.source_params.name}`]
    }
    if (source.source_params.name === 's3_public_v0') {
      return [`S3: ${source.source_params.bucket_name}`]
    }
    return []
  })
}
