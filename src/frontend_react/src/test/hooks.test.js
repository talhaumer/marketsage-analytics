import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useAnalysis } from '../hooks/useAnalysis'

vi.mock('../api/client', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}))

import client from '../api/client'

describe('useAnalysis', () => {
  beforeEach(() => vi.clearAllMocks())

  it('starts in idle state', () => {
    const { result } = renderHook(() => useAnalysis())
    expect(result.current.status).toBe('idle')
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('transitions to done on successful response', async () => {
    client.post.mockResolvedValueOnce({
      data: { success: true, data: { final_analysis: 'Bull market ahead' } },
    })
    const { result } = renderHook(() => useAnalysis())
    await act(async () => {
      await result.current.run({ question: 'test', symbols: ['AAPL'] })
    })
    expect(result.current.status).toBe('done')
    expect(result.current.result.data.final_analysis).toBe('Bull market ahead')
  })

  it('transitions to error on network failure', async () => {
    client.post.mockRejectedValueOnce(new Error('Network Error'))
    const { result } = renderHook(() => useAnalysis())
    await act(async () => {
      await result.current.run({ question: 'test', symbols: [] })
    })
    expect(result.current.status).toBe('error')
    expect(result.current.error).toBeTruthy()
  })

  it('transitions to error when success is false', async () => {
    client.post.mockResolvedValueOnce({
      data: { success: false, error: 'Agent failed' },
    })
    const { result } = renderHook(() => useAnalysis())
    await act(async () => {
      await result.current.run({ question: 'test', symbols: [] })
    })
    expect(result.current.status).toBe('error')
    expect(result.current.error).toBe('Agent failed')
  })

  it('reset returns to idle', async () => {
    client.post.mockResolvedValueOnce({
      data: { success: true, data: { final_analysis: 'Done' } },
    })
    const { result } = renderHook(() => useAnalysis())
    await act(async () => {
      await result.current.run({ question: 'test', symbols: [] })
    })
    act(() => result.current.reset())
    expect(result.current.status).toBe('idle')
    expect(result.current.result).toBeNull()
  })
})
