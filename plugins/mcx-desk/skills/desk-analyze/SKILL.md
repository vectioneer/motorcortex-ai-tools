---
name: desk-analyze
description: Analyze signals already plotted in a Motorcortex Desk tab — statistics (mean, std, min/max, RMS, peak-to-peak) over any time window, FFT spectra and dominant frequency, plus overshoot, settling time, rise time and lag between traces, and snapshot values. Use when the user says "measure the step response", "what's the peak", "how noisy is this", "what frequency is that ringing at", "show me the spectrum", "how much delay between the signals". For exploring the parameter tree, use param-explore; for plotting, desk-plot.
review-by: 2027-03-04
---

Analyze plotted Motorcortex Desk signals: "$ARGUMENTS"

Requires traces already plotted (use `desk-plot` otherwise) and a connected
hub tab.

Parse the arguments for:
- **traces**: which plotted signals to analyze (default: all)
- **metric**: peak, overshoot, settling time, rise time, period/frequency,
  mean/RMS, lag between two traces — infer from phrasing
- **window**: time range of interest, if any

## Step 1: Freeze the data

`list_traces` to confirm what is plotted.

One `read_statistics` or `read_spectrum` call is already a consistent snapshot
— it computes inside the tab over one buffer state — so a single metric does
not need a pause. `pause` first when the answer spans **several** calls that
must describe the same instant: comparing two traces, or a statistic and the
samples behind it. Remember to `resume` at the end.

## Step 2: Ask for the metric before fetching samples

Three tools compute over the **full** buffer inside the tab. Prefer them: they
are exact, one call, and no data crosses the bridge.

`read_statistics(path, channel?, from?, to?, quantiles?)` — n, mean, std
(population), min, max, rms, peak-to-peak, plus `tMin`/`tMax` (when the
extremes occurred), `xFirst`/`xLast`/`span` (the data's own extent inside the
window) and `rate` (mean sample rate, Hz). Add `quantiles` for median/q1/q3.
This is the answer to "what's the peak", "how noisy is this", "what's the
average".

`read_spectrum(path, channel?, from?, to?, maxPoints?)` — the FFT: `peak`
{freq, magDb} is the dominant frequency, with `fs`, `nyquist`, `bins`,
`resolution` (bin width) and `fMin` (lowest representable frequency). This is
the answer to "what frequency is it ringing at", and it beats counting zero
crossings by hand.

`show_spectrum(path, channel?, from?, to?)` — draws it in the Spectrum tab so
the **user** sees the curve. Use it when they asked to *see* a frequency plot,
not just be told a number; use `read_spectrum` when you need the numbers to
reason over. It shows one signal at a time, so pass `channel` for an array
parameter.

`from`/`to` are plot x seconds, either end omittable, and default to the whole
buffer — so windowing a metric costs no extra call.

Two things to check before trusting a spectrum: `resolution`, because a short
window cannot resolve a slow oscillation, and `fMin`, because nothing slower
than that is visible however long the window looks. The mean is removed before
the transform, so a constant offset never shows up as a peak, and `magDb` is
amplitude in dB, not power.

## Step 3: Fetch samples only for what has no tool

`read_samples(path, channel?, from?, to?, maxPoints=...)` returns
`{total, points: [{x, y}]}` with x in trace seconds. Points are **uniformly
decimated**, so compute a metric from them only when no tool covers it:

- **overshoot**: (max − final) / (final − initial), needs a clear step
- **settling time**: first time the signal stays within a band (default ±2%)
  of the final value
- **rise time**: 10% → 90% of the step
- **lag between traces**: shift of best alignment (cross-correlate or match
  characteristic edges)

Do not hand-compute mean, RMS, min, max, std or peak-to-peak from these
points: decimation drops samples, so the answer is an approximation of a
number `read_statistics` gives exactly. Likewise period/frequency — take
`read_spectrum`'s `peak` over counting crossings in a decimated series.

For sharp-edge metrics (rise time, lag) request more points (cap 5000) or
narrow the window with `from`/`to` and read again. State the window and sample
count used; decimation limits precision — say so when it matters.

For a plain "what is the value now", `read_values(paths=[...])` is enough —
no pause needed.

Custom signals (`formulas/<name>` in `list_traces`, carrying a `formula`
field) work with all four of these tools. `read_values` will not work on them:
they are computed in the plot, so the controller has no such parameter. An
expression over a whole array fans out to one trace per element, so a
channel-less call returns a `channels` array — the same shape as a real array
parameter. When reporting on one, quote its expression: the number came from
arithmetic in the browser, not from the controller.

If a metric needs a quantity nobody publishes — a tracking error, a magnitude
from components — check the tree first (`search_parameters`), and only if it is
genuinely absent create it with `add_custom_signal` (see `desk-plot`) and read
it back once samples have accumulated. Computing it yourself from two
`read_samples` results is equally valid and needs no trace; prefer that for a
one-off number, and a custom signal when the user wants to *see* it.

## Step 4: Report and restore

Report values with units where known (path names often hint: Position,
Velocity, Torque). `resume` if you paused. Offer `desk-capture` for a
screenshot or CSV of the analyzed window, and `show_spectrum` when a frequency
result is easier to see than to read.

## Notes

- Buffered samples only exist for plotted traces — plot first, then measure.
  That includes the statistics and spectrum tools: they read the same buffers.
- `n` from `read_statistics` counts only finite samples, so a controller
  publishing NaN makes `n` smaller than `total` from `read_samples`. Compare
  the two before concluding a window is short of data.
- The buffer is finite; long-ago data may have scrolled out. For long
  captures, export CSV early (`desk-capture`) and analyze the file instead.
- The tab may be shared with other Claude sessions, and `pause` stops the
  plot for all of them. Keep the pause short and always `resume`.
- After a controller restart or redeploy, calls fail with "not connected to
  controller" or find no data in range. Reconnect and re-add the traces as in
  `desk-plot` Step 1 before capturing or measuring again — the buffer from
  before the restart is gone.
- If a tool reports "no hub tab connected" or "port in use", call
  `bridge_status` first — it says which session owns the bridge and whether
  a tab is attached, instead of leaving you to guess.
