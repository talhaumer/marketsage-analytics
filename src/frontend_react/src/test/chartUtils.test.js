import { describe, it, expect } from 'vitest'
import { mergeByDate, computeRSI, computeReturn } from '../utils/chartUtils'

describe('mergeByDate', () => {
  it('merges two symbols by date on the given field', () => {
    const data = {
      AAPL: [
        { date: '2024-01-01', close: 100, volume: 1000 },
        { date: '2024-01-02', close: 102, volume: 1100 },
      ],
      MSFT: [
        { date: '2024-01-01', close: 200, volume: 2000 },
        { date: '2024-01-02', close: 205, volume: 2100 },
      ],
    }
    const result = mergeByDate(data, 'close')
    expect(result).toHaveLength(2)
    expect(result[0]).toEqual({ date: '2024-01-01', AAPL: 100, MSFT: 200 })
    expect(result[1]).toEqual({ date: '2024-01-02', AAPL: 102, MSFT: 205 })
  })

  it('returns sorted by date ascending', () => {
    const data = {
      X: [
        { date: '2024-01-03', close: 10 },
        { date: '2024-01-01', close: 8 },
      ],
    }
    const result = mergeByDate(data, 'close')
    expect(result[0].date).toBe('2024-01-01')
    expect(result[1].date).toBe('2024-01-03')
  })
})

describe('computeRSI', () => {
  it('returns nulls for the first 14 periods', () => {
    const closes = Array.from({ length: 14 }, (_, i) => 100 + i)
    const rsi = computeRSI(closes)
    expect(rsi).toHaveLength(14)
    expect(rsi.every((v) => v === null)).toBe(true)
  })

  it('returns values between 0 and 100 for period 15+', () => {
    const closes = Array.from({ length: 25 }, (_, i) => 100 + Math.sin(i) * 5)
    const rsi = computeRSI(closes)
    const values = rsi.filter((v) => v !== null)
    expect(values.length).toBeGreaterThan(0)
    values.forEach((v) => {
      expect(v).toBeGreaterThanOrEqual(0)
      expect(v).toBeLessThanOrEqual(100)
    })
  })

  it('returns 100 when all price moves are gains', () => {
    const closes = Array.from({ length: 20 }, (_, i) => 100 + i)
    const rsi = computeRSI(closes)
    expect(rsi[rsi.length - 1]).toBe(100)
  })

  it('returns 0 when all price moves are losses', () => {
    const closes = Array.from({ length: 20 }, (_, i) => 200 - i)
    const rsi = computeRSI(closes)
    expect(rsi[rsi.length - 1]).toBe(0)
  })
})

describe('computeReturn', () => {
  it('computes percent return correctly', () => {
    const rows = [{ close: 100 }, { close: 50 }, { close: 110 }]
    expect(computeReturn(rows)).toBe(10)
  })

  it('returns 0 for empty or single-element arrays', () => {
    expect(computeReturn([])).toBe(0)
    expect(computeReturn([{ close: 100 }])).toBe(0)
  })

  it('handles negative return', () => {
    const rows = [{ close: 100 }, { close: 90 }]
    expect(computeReturn(rows)).toBe(-10)
  })
})
