exports.handler = async function(event) {
  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ test: 'ok', key: process.env.ANTHROPIC_API_KEY ? 'present' : 'missing' })
  };
};
