# Getting Started with Mistral OCR

This guide walks you through obtaining a Mistral API key and configuring it for use with the OCR processor script.

## Step 1: Create a Mistral Account

1. Go to [console.mistral.ai](https://console.mistral.ai/)
2. Click **Sign Up** (or **Sign In** if you have an account)
3. You can sign up with:
   - Email and password
   - Google account
   - GitHub account

## Step 2: Add Billing (Required for API Access)

Mistral requires a payment method to use the API:

1. Go to **Billing** in the left sidebar
2. Click **Add Payment Method**
3. Enter your credit card details
4. Add credits to your account (minimum ~$5)

> **Note:** Check current pricing at [mistral.ai/pricing](https://mistral.ai/pricing/)

## Step 3: Create an API Key

1. Go to **API Keys** in the left sidebar
2. Click **Create new key**
3. Give it a descriptive name (e.g., "OCR Skill")
4. Copy the key immediately - it won't be shown again!

Your key looks like: `aBc123XyZ...` (about 32 characters)

## Step 4: Configure Your API Key

### Option A: Pass via --api-key (Recommended)

Pass the key directly when running the script:

```bash
python scripts/ocr_processor.py --input doc.pdf --output doc.md --api-key "your-api-key-here"
```

### Option B: Environment Variable

```bash
# Linux/macOS
export MISTRAL_API_KEY="your-api-key-here"

# Windows PowerShell
$env:MISTRAL_API_KEY = "your-api-key-here"
```

### Option C: Settings File (Claude Code / opencode)

Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "MISTRAL_API_KEY": "your-api-key-here"
  }
}
```

## Step 5: Verify It Works

```bash
python scripts/ocr_processor.py --input path/to/test.jpg
```

If successful, extracted text will be printed to stdout.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Unauthorized" error | Check your API key is correct and has credits |
| "No credits" error | Add billing/credits in Mistral console |
| Key not recognized | Ensure no extra spaces, quotes are correct |
| Rate limited | Wait a minute and try again |

## Pricing Overview

| Service | Cost |
|---------|------|
| OCR (per 1,000 pages) | ~$2.00 |
| Batch API discount | 50% off |

> **Tip:** Check [mistral.ai/pricing](https://mistral.ai/pricing/) for current rates.

## Next Steps

Once your key is configured:

1. Try extracting text from an image
2. Convert a PDF to Markdown
3. See [guide.md](guide.md) for complete examples
