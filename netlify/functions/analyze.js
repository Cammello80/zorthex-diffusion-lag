const https = require('https');

exports.handler = async function(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const { query } = JSON.parse(event.body);
    const apiKey = process.env.ANTHROPIC_API_KEY;
    
    if (!apiKey) {
      return { statusCode: 500, body: JSON.stringify({ error: 'No API key' }) };
    }

    const prompt = `Analyze "${query}" using Zorthex v1.1 framework. Respond ONLY with valid JSON:
{
  "title": "${query}",
  "tStart": "Jan 2010",
  "tPeak": "Jan 2020",
  "L": 120,
  "peakScore": 75,
  "monthsAbove": 18,
  "currentScore": 35,
  "status": "structural",
  "chartData": [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,75,60,45,35,30,35],
  "src1": "Google Trends analysis for ${query}.",
  "src2": "Wikipedia pageviews analysis for ${query}.",
  "src3": "Reddit community analysis for ${query}.",
  "interpretation": "Analysis of ${query} based on Zorthex v1.1 framework.",
  "monitor": "Monitor developments in ${query}."
}`;

    const body = JSON.stringify({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1500,
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
              resolve({ statusCode: 500, body: JSON.stringify({ error: parsed.error.message }) });
              return;
            }
            const text = parsed.content[0].text;
            const clean = text.replace(/```json|```/g, '').trim();
            const result = JSON.parse(clean);
            resolve({
              statusCode: 200,
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(result)
            });
          } catch (err) {
            resolve({ statusCode: 500, body: JSON.stringify({ error: err.message, raw: data.substring(0, 500) }) });
          }
        });
      });

      req.on('error', (err) => {
        resolve({ statusCode: 500, body: JSON.stringify({ error: err.message }) });
      });

      req.write(body);
      req.end();
    });
  } catch (err) {
    return { statusCode: 500, body: JSON.stringify({ error: err.message }) };
  }
};
