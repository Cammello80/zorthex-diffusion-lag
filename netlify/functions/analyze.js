const https = require('https');

exports.handler = async function(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  // CORS headers
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    const { query } = JSON.parse(event.body);
    const apiKey = process.env.ANTHROPIC_API_KEY;

    if (!apiKey) {
      return { statusCode: 500, headers, body: JSON.stringify({ error: 'No API key configured' }) };
    }

    const prompt = `You are applying the Zorthex v1.1 framework to analyze the public attention diffusion lag for: "${query}"

Zorthex definitions:
- t_start: first relevant public appearance
- t_peak: first month Google Trends reached ≥25/100 sustained
- L = t_peak - t_start in months
- STRUCTURAL: ≥25/100 for 12+ consecutive months
- OBSERVATION: above threshold but fewer than 12 consecutive months
- BUBBLE: reached high attention but dropped below threshold without consolidating

Respond ONLY with valid JSON, no other text, no markdown:

{
  "title": "clean display name",
  "tStart": "approximate month/year",
  "tPeak": "approximate month/year of first major peak",
  "L": number,
  "peakScore": number 0-100,
  "monthsAbove": number,
  "currentScore": number 0-100 estimated May 2026,
  "status": "structural" or "observation" or "bubble",
  "chartData": [array of 80 numbers 0-100 representing attention curve from tStart to May 2026],
  "src1": "2-3 sentences Google Trends analysis",
  "src2": "2-3 sentences Wikipedia pageviews analysis",
  "src3": "2-3 sentences Reddit community analysis",
  "interpretation": "3-4 sentences observational Zorthex tone, no hype",
  "monitor": "2-3 sentences on what signals to watch next",
  "whatItMeans": "One factual incipit sentence with peak value peak date and current score. Then the text WHAT IT MEANS on its own. Then 3-4 sentences: observational cold precise. Where is this phenomenon in its public cycle. No prescriptions no recommendations. End with: These values reflect observed attention patterns — not projections."
}`;

    const body = JSON.stringify({
      model: 'claude-opus-4-5',
      max_tokens: 2000,
      messages: [{ role: 'user', content: prompt }]
    });

    return new Promise((resolve) => {
      const options = {
        hostname: 'api.anthropic.com',
        path: '/v1/messages',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey,
          'anthropic-version': '2023-06-01',
          'Content-Length': Buffer.byteLength(body)
        }
      };

      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
          try {
            const parsed = JSON.parse(data);
            if (parsed.error) {
              resolve({ statusCode: 500, headers, body: JSON.stringify({ error: parsed.error.message }) });
              return;
            }
            const text = parsed.content[0].text;
            const clean = text.replace(/```json|```/g, '').trim();
            const result = JSON.parse(clean);
            resolve({ statusCode: 200, headers, body: JSON.stringify(result) });
          } catch (err) {
            resolve({ statusCode: 500, headers, body: JSON.stringify({ error: err.message, raw: data.substring(0, 500) }) });
          }
        });
      });

      req.on('error', (err) => {
        resolve({ statusCode: 500, headers, body: JSON.stringify({ error: err.message }) });
      });

      req.write(body);
      req.end();
    });

  } catch (err) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: err.message }) };
  }
};
