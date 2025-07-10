import React, { useState } from "react";
import {
  ThemeProvider,
  CssBaseline,
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Paper,
  Divider,
} from "@mui/material";
import theme from "@safaricom/sui";

function App() {
  const [msisdn, setMsisdn] = useState("");
  const [amount, setAmount] = useState("");
  const [response, setResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResponse(null); // clear previous

    try {
      const res = await fetch("http://127.0.0.1:8000/stkpush", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ msisdn, amount: parseInt(amount) }),
      });

      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ error: "⚠️ Failed to connect to backend." });
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: "100vh",
          bgcolor: "#e8f5e9", // light Safaricom green
          py: 6,
        }}
      >
        <Container maxWidth="sm">
          <Paper elevation={4} sx={{ p: 4, borderRadius: 3 }}>
            <Typography variant="h4" color="primary" gutterBottom align="center">
              💸 Safaricom STK Push
            </Typography>

            <Typography variant="subtitle1" align="center" color="text.secondary" mb={3}>
              Enter your phone number and amount to initiate a secure STK push request.
            </Typography>

            <form onSubmit={handleSubmit}>
              <TextField
                label="Phone Number (e.g. 2547XXXXXXXX)"
                variant="outlined"
                fullWidth
                margin="normal"
                value={msisdn}
                onChange={(e) => setMsisdn(e.target.value)}
                required
              />

              <TextField
                label="Amount (KES)"
                type="number"
                variant="outlined"
                fullWidth
                margin="normal"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />

              <Box mt={3} textAlign="center">
                <Button variant="contained" color="primary" type="submit" size="large">
                  Send STK Push
                </Button>
              </Box>
            </form>

            {response && (
              <>
                <Divider sx={{ my: 4 }} />

                <Typography
                  variant="h6"
                  gutterBottom
                  color={response.error ? "error" : "success.main"}
                >
                  {response.error ? "❌ Error" : "✅ Success"}
                </Typography>

                <Box
                  sx={{
                    backgroundColor: "#f0f4f8",
                    border: "1px solid #cfd8dc",
                    borderRadius: 2,
                    padding: 2,
                    maxHeight: "300px",
                    overflow: "auto",
                    fontFamily: "monospace",
                    fontSize: "0.95rem",
                    whiteSpace: "pre-wrap",
                    wordWrap: "break-word",
                    boxShadow: 1,
                  }}
                >
                  <pre style={{ margin: 0 }}>
                    {JSON.stringify(response, null, 2)}
                  </pre>
                </Box>
              </>
            )}
          </Paper>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;
