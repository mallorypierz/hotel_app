<script setup>
defineProps({ evidence: { type: Object, required: true }, status: { type: String, default: '' } })
const pretty = (value) => JSON.stringify(value, null, 2)
const validation = {
  not_reached: 'Retrieval not reached', checking: 'Validation started',
  passed_read_only_and_record_verification: 'Passed read-only validation and record verification',
  rejected_or_limit_exceeded: 'Query rejected, a limit exceeded, or record verification failed; no answer produced',
}
</script>

<template>
  <details class="evidence">
    <summary>How this answer was produced</summary>
    <h3>Original question</h3>
    <p>{{ evidence.question }}</p>
    <h3>Provider / model</h3>
    <p>{{ evidence.provider }} / {{ evidence.model }}</p>
    <h3>Proposed SQL (read-only evidence)</h3>
    <pre>{{ evidence.proposal?.sql || (status === 'clarification' ? 'Query paused for clarification. Update the question using the guidance above, then send again.' : 'No SQL proposal available. See the request status above.') }}</pre>
    <h3>Bound parameters</h3>
    <pre>{{ pretty(evidence.proposal?.parameters || []) }}</pre>
    <h3>Validation outcome</h3>
    <p>{{ validation[evidence.validation] || evidence.validation }}</p>
    <h3>Retrieved records</h3>
    <p>{{ evidence.retrieval?.row_count ?? 0 }} rows returned; maximum {{ evidence.retrieval?.row_limit ?? 50 }} rows / {{ evidence.retrieval?.byte_limit ?? 24576 }} bytes.</p>
    <p>Complete: {{ evidence.retrieval?.complete ? 'yes' : 'no' }}. Truncated: {{ evidence.retrieval?.truncated ? 'yes' : 'no' }}.</p>
    <p v-if="evidence.retrieval?.scope">
      {{ evidence.retrieval.scope }}
    </p>
    <ol v-if="evidence.retrieved_records?.length">
      <li
        v-for="(record, index) in evidence.retrieved_records"
        :key="index"
      >
        <dl>
          <template
            v-for="(value, field) in record"
            :key="field"
          >
            <dt>{{ field }}</dt><dd>{{ value ?? 'Not provided' }}</dd>
          </template>
        </dl>
      </li>
    </ol>
    <p v-else>
      No records returned.
    </p>
    <h3>Model request stages</h3>
    <ul>
      <li
        v-for="(call, index) in evidence.model_calls"
        :key="index"
      >
        {{ call.stage }}: {{ call.status }}
      </li>
    </ul>
    <p>SQL is evidence only. It cannot be edited or executed here.</p>
  </details>
</template>

<style scoped>
.evidence { margin-top: 24px; padding: 20px; border: 1px solid #c9d4cd; border-radius: 14px; background: #fff; overflow-wrap: anywhere; }
summary { cursor: pointer; font-weight: 700; min-height: 44px; display: list-item; padding: 12px 0; }
summary:focus-visible { outline: 3px solid #d66f3d; outline-offset: 4px; }
h3 { margin: 24px 0 10px; font-size: 1.1rem; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f0f2ed; padding: 16px; border-radius: 8px; font-size: .875rem; }
ol { padding-left: 24px; } li { margin-bottom: 12px; } dl { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 2fr); gap: 6px 16px; border-bottom: 1px solid #d7dedb; padding-bottom: 12px; } dt { font-weight: 700; } dd { margin: 0; }
@media (max-width: 600px) { dl { grid-template-columns: 1fr; } dd { margin-bottom: 8px; } .evidence { padding: 16px; } }
</style>
