exports.handler = async function(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const { query } = JSON.parse(event.body);

  const prompt = `You are applying the Zorthex v1.1 framework to analyze the public attention diffusion lag for: "${query}"

The Zorthex framework definitions:
- t_start: first relevant public appearance of the phenomenon
- t_peak: first month where Google Trends reached a sustained threshold of ≥25/100 for at least one month
- L = t_peak - t_start (in months). This is the diffusion lag.
- Classification:
  * STRUCTURAL: sustained ≥25/100 for 12+ consecutive months (mainstream consolidated)
  * OBSERVATION: above threshold but fewer than 12 consecutive months (forming)
  * BUBBLE: reached high attention but dropped below threshold without consolidating

Analyze "${query}" and respond ONLY with valid JSON, no other text:

{
  "title": "clean display name",
  "tStart": "approximate month/year of first public emergence",
  "tPeak": "approximate month/year of first major attention peak",
  "L": number of months between tStart and tPeak,
  "peakScore": estimated Google Trends peak score 0-100,
  "monthsAbove": estimated months above threshold of 25,
  "currentScore": estimated current Google Trends score May 2026 (0-100),
  "status": "structural" or "observation" or "bubble",
  "chartData": array of 80 numbers 0-100 representing estimated attention curve over time from tStart to May 2026,
  "src1": "2-3 sentence Google Trends analysis",
  "src2": "2-3 sentence Wikipedia pageviews analysis",
  "src3": "2-3 sentence Reddit community analysis",
  "interpretation": "3-4 sentence interpretation in Zorthex tone",
  "monitor": "2-3 sentence: what specific events or signals to watch next"
}`;

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1500,
        messages: [{ role: 'user', content: prompt }]
      })
    });

    const data = await response.json();
    const text = data.content[0].text;
    const clean = text.replace(/```json|```/g, '').trim();
    const parsed = JSON.parse(clean);

    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(parsed)
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: err.message })
    };
  }
};
