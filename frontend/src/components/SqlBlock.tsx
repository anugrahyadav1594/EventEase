/** Lightweight SQL syntax highlighter (no external dependency). */
import { Fragment } from 'react'

const KEYWORDS = new Set([
  'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'ORDER', 'HAVING', 'JOIN', 'INNER', 'LEFT', 'RIGHT',
  'FULL', 'OUTER', 'CROSS', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'IS', 'NULL', 'LIKE', 'BETWEEN',
  'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ROUND',
  'COALESCE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'ALTER', 'DROP',
  'TABLE', 'VIEW', 'INDEX', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'CONSTRAINT', 'UNIQUE',
  'CHECK', 'DEFAULT', 'EXISTS', 'INTERSECT', 'EXCEPT', 'UNION', 'ALL', 'LIMIT', 'OFFSET', 'WITH',
  'CURRENT_DATE', 'CURRENT_TIMESTAMP', 'ASC', 'DESC', 'DISTINCT', 'TRIM', 'UPPER', 'LOWER', 'LENGTH',
  'CHAR_LENGTH', 'SUBSTRING', 'CONCAT', 'INSTR', 'POSITION',
])

const FUNCTIONS = new Set([
  'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ROUND', 'COALESCE', 'IFNULL', 'NOW', 'CURDATE',
  'TRIM', 'UPPER', 'LOWER', 'LENGTH', 'CHAR_LENGTH', 'SUBSTRING', 'CONCAT', 'INSTR', 'POSITION',
])

const tokenRegex = /(--[^\n]*)|('(?:[^']|'')*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)/g

export default function SqlBlock({ sql, inline = false }: { sql: string; inline?: boolean }) {
  const parts: JSX.Element[] = []
  let lastIndex = 0
  let key = 0

  tokenRegex.lastIndex = 0
  let match: RegExpExecArray | null
  while ((match = tokenRegex.exec(sql)) !== null) {
    if (match.index > lastIndex) {
      parts.push(<Fragment key={key++}>{sql.slice(lastIndex, match.index)}</Fragment>)
    }
    const [token, comment, text, number, word] = match
    if (comment) {
      parts.push(
        <span className="sql-comment" key={key++}>
          {token}
        </span>,
      )
    } else if (text) {
      parts.push(
        <span className="sql-string" key={key++}>
          {token}
        </span>,
      )
    } else if (number) {
      parts.push(
        <span className="sql-number" key={key++}>
          {token}
        </span>,
      )
    } else if (word) {
      const upper = word.toUpperCase()
      if (KEYWORDS.has(upper)) {
        parts.push(
          <span className="sql-keyword" key={key++}>
            {token}
          </span>,
        )
      } else if (FUNCTIONS.has(upper)) {
        parts.push(
          <span className="sql-function" key={key++}>
            {token}
          </span>,
        )
      } else {
        parts.push(<Fragment key={key++}>{token}</Fragment>)
      }
    }
    lastIndex = match.index + token.length
  }

  if (lastIndex < sql.length) {
    parts.push(<Fragment key={key++}>{sql.slice(lastIndex)}</Fragment>)
  }

  return <pre className={`sql-block ${inline ? 'sql-block--inline' : ''}`}>{parts}</pre>
}
