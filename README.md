# AI Call Agent - Resilient Voice AI System

A production-ready AI voice agent system with robust error handling, automatic retry mechanisms, and circuit breaker patterns to ensure reliable operation even when external services fail.

## Table of Contents
- [Overview](#overview)
- [Architecture Decisions](#architecture-decisions)
- [Error Flow](#error-flow)
- [Retry & Circuit Breaker Behavior](#retry--circuit-breaker-behavior)
- [Alerting Logic](#alerting-logic)
- [Installation](#installation)
- [Usage](#usage)
- [Example Logs](#example-logs)
- [Project Structure](#project-structure)

---

## Overview

This project implements a resilient AI call agent that processes voice calls through three main services:
1. **STT (Speech-to-Text)** - Converts audio to text
2. **LLM (Large Language Model)** - Generates intelligent responses
3. **TTS (Text-to-Speech)** - Converts text back to audio

The system includes comprehensive error handling to ensure reliability in production environments.

---

## Architecture Decisions

### **1. Layered Error Handling Architecture**
```
┌─────────────────────────────────────┐
│        Call Agent (Main)            │  ← Orchestrates entire flow
├─────────────────────────────────────┤
│     Circuit Breaker Layer           │  ← Prevents cascading failures
├─────────────────────────────────────┤
│     Retry Manager Layer             │  ← Handles transient errors
├─────────────────────────────────────┤
│  STT Service │ LLM Service │ TTS    │  ← External service calls
└─────────────────────────────────────┘
```

### **Key Design Decisions:**

#### **a) Custom Exception Hierarchy**
- **Transient Errors** (TimeoutError, NetworkError, RateLimitError) → Can be retried
- **Permanent Errors** (AuthenticationError, InvalidPayloadError) → Should NOT be retried
- This separation prevents wasting resources on unrecoverable errors

#### **b) Circuit Breaker Pattern**
- Prevents cascading failures when a service is down
- Three states: CLOSED → OPEN → HALF_OPEN
- Fails fast when circuit is OPEN, saving time and resources

#### **c) Exponential Backoff**
- Initial delay: 5 seconds
- Backoff multiplier: 2x
- Sequence: 5s → 10s → 20s
- Prevents overwhelming recovering services

#### **d) Separation of Concerns**
Each component has a single responsibility:
- `exceptions.py` - Error classification
- `retry_manager.py` - Retry logic
- `circuit_breaker.py` - Circuit breaker state management
- `logger.py` - Logging
- `alerts.py` - Critical error notifications
- `call_agent.py` - Orchestration

---

## Error Flow

### **Complete Error Handling Flow Diagram**
```
                     ┌─────────────────┐
                     │  Call Received  │
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │   STT Service   │
                     └────────┬────────┘
                              │
                    ┌─────────▼──────────┐
                    │   Error Occurs?    │
                    └─────────┬──────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
      ┌───────▼────────┐            ┌────────▼─────────┐
      │ Transient Error│            │ Permanent Error  │
      │ (Timeout, 503) │            │ (401, 400, 404)  │
      └───────┬────────┘            └────────┬─────────┘
              │                               │
      ┌───────▼────────┐                     │
      │ Retry Manager  │                     │
      │ - Attempt 1/3  │                     │
      │ - Wait 5s      │                     │
      │ - Attempt 2/3  │                     │
      │ - Wait 10s     │                     │
      │ - Attempt 3/3  │                     │
      └───────┬────────┘                     │
              │                               │
      ┌───────▼────────┐                     │
      │ Still Failing? │                     │
      └───────┬────────┘                     │
              │                               │
              ├───────────────────────────────┘
              │
      ┌───────▼─────────────┐
      │  Circuit Breaker    │
      │  Failure Count: 3   │
      │  State: OPEN        │
      └───────┬─────────────┘
              │
      ┌───────▼─────────────┐
      │  Log Error          │
      │  Send Alert         │
      │  Fail Fast (Future) │
      └─────────────────────┘
```

### **Error Flow Steps:**

1. **Error Detection** → Exception is caught and classified as Transient or Permanent
2. **Retry Decision** → Transient errors enter retry loop, Permanent errors skip to logging
3. **Circuit Breaker Update** → Failure count incremented; circuit opens after threshold
4. **Logging** → All errors logged to `logs/error_log.json`
5. **Alerting** → Critical errors trigger alerts in `logs/alerts.json`

---

## Retry & Circuit Breaker Behavior

### **Retry Manager Behavior**

#### **Configuration:**
```yaml
retry:
  initial_delay: 5          # Start with 5 second delay
  backoff_multiplier: 2     # Double delay each retry
  max_attempts: 3           # Try maximum 3 times
```

#### **Example Retry Sequence:**
```
Attempt 1: Immediate call → FAILS
Wait: 5 seconds
Attempt 2: Retry call → FAILS
Wait: 10 seconds (5 × 2)
Attempt 3: Final retry → FAILS
Result: Raise exception
```

#### **Retry Logic:**
- ✅ **Retries**: TimeoutError, NetworkError, ServiceUnavailableError (503), RateLimitError (429)
- ❌ **Does NOT Retry**: AuthenticationError (401/403), InvalidPayloadError (400), ResourceNotFoundError (404)

---

### **Circuit Breaker Behavior**

#### **Configuration:**
```yaml
circuit_breaker:
  failure_threshold: 3      # Open circuit after 3 failures
  timeout: 60              # Wait 60 seconds before trying again
```

#### **State Transitions:**

**1. CLOSED State (Normal Operation)**
```
✅ Requests flow normally
✅ Failure count resets on success
⚠️  After 3 failures → Transition to OPEN
```

**2. OPEN State (Service Down)**
```
⛔ All requests fail immediately
⛔ No actual service calls made
⏱️  After 60 seconds → Transition to HALF_OPEN
```

**3. HALF_OPEN State (Testing Recovery)**
```
🔄 Allow 1 test request
✅ If success → Transition to CLOSED
❌ If failure → Back to OPEN
```

#### **Example Circuit Breaker Flow:**
```
Call 1: STT fails (Count: 1, State: CLOSED)
Call 2: STT fails (Count: 2, State: CLOSED)
Call 3: STT fails (Count: 3, State: OPEN)  ← Circuit opens here!
Call 4: Immediate failure (State: OPEN)     ← No actual call made
Call 5: Immediate failure (State: OPEN)
[60 seconds pass]
Call 6: Test request (State: HALF_OPEN)
  → If succeeds: Circuit closes
  → If fails: Back to OPEN state
```

---

## 🚨 Alerting Logic

### **Alert Severity Levels**

| Severity | Trigger Condition | Example |
|----------|-------------------|---------|
| **LOW** | Single transient error | One timeout error |
| **MEDIUM** | Multiple retries exhausted | All 3 retries failed |
| **HIGH** | Permanent error or Circuit OPEN | Authentication failure, Circuit breaker opened |
| **CRITICAL** | System-wide failure | Multiple services down |

### **Alert Structure:**
```json
{
  "timestamp": "2025-01-30T12:34:56",
  "severity": "HIGH",
  "service_name": "STT",
  "error_message": "Authentication failed",
  "status": "UNRESOLVED"
}
```

### **Alert Flow:**
```
Error Occurs → Classified by Type → Logged → Alert Generated (if critical)
     ↓              ↓                  ↓            ↓
Transient/     Severity Level    error_log.json  alerts.json
Permanent      Determined
```

---

## 🚀 Installation

### **Prerequisites:**
- Python 3.8 or higher
- Git

### **Steps:**

1. **Clone the repository:**
```bash
   git clone https://github.com/YOUR_USERNAME/ai-call-agent.git
   cd ai-call-agent
```

2. **Create virtual environment:**
```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Mac/Linux:
   source venv/bin/activate
```

3. **Install dependencies:**
```bash
   pip install pyyaml
```

---

## 💻 Usage

### **Run Demo:**
```bash
python demo.py
```

### **Expected Output:**

The demo simulates 5 calls with 30% failure rate for each service. You'll see:
- Retry attempts with exponential backoff
- Circuit breaker state transitions
- Success and failure logs

---

## 📊 Example Logs

### **Console Output:**

<!-- PASTE SCREENSHOT HERE -->
<!-- Console execution output screenshots -->

<p align="center">
  <img src="https://github.com/user-attachments/assets/3ca962a2-1ec9-48c2-baf3-edbd576c288b" width="90%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/23a05a2a-786f-48af-b9a8-696b0f651061" width="90%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/250ec97b-d113-4186-a3ed-2cc0587cd520" width="90%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/0f18686e-1908-4ffd-849e-4136c2ab8c9a" width="90%" />
</p>




**Key Points in Output:**
- Services initialize successfully
- Calls proceed through STT → LLM → TTS pipeline
- Retries triggered on failures with exponential delays
- Circuit breaker opens after threshold failures
- Final system status shows circuit states

---

## **Error Log (error_log.json):**
### Auto generates when run program [demo.py]
<p align="center">
  <img src="https://github.com/user-attachments/assets/c282eca8-c3ca-417f-8f7b-1240890a9b8c" width="90%" />
</p>


---

## **Alert Log (alerts.json):**
### Auto generates when run program [demo.py]
<p align="center">
  <img src="https://github.com/user-attachments/assets/79db35e9-4165-4be7-96e4-b11e1ffb0f3c" width="90%" />
</p>



---

## 📁 Project Structure
### 1> Here the Config folder not needed to run the program
### 2> The logs Automaticaly created when we run the demo.py 
```
ai-call-agent/
├── config/                     # Configuration folder (empty)
├── logs/                       # Runtime logs (generated)
│   ├── error_log.json         # All error events
│   └── alerts.json            # Critical alerts
│
├── alerts.py                   # Alert system implementation
├── call_agent.py              # Main orchestrator
├── circuit_breaker.py         # Circuit breaker pattern
├── config.yaml                # System configuration
├── demo.py                    # Demo script
├── exceptions.py              # Custom exception hierarchy
├── logger.py                  # Error logging system
├── mock_services.py           # Mock STT/LLM/TTS services
├── retry_manager.py           # Retry with exponential backoff
│
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```
<p align="center">
  <img src="https://github.com/user-attachments/assets/bcc2da70-7db5-46b4-baae-f0a9a21aee89" width="60%" />
</p>


---

## 🧪 Test Cases & Simulations

### **Included Test Scenarios:**

The `demo.py` script simulates various failure scenarios:

1. **Scenario 1: Transient Errors**
   - Random timeout errors (30% probability)
   - Tests retry mechanism
   - Expected: 1-3 retries, then success

2. **Scenario 2: Rate Limiting**
   - Simulates 429 errors
   - Tests exponential backoff
   - Expected: Increasing delays between retries

3. **Scenario 3: Circuit Breaker**
   - Multiple consecutive failures
   - Tests circuit opening
   - Expected: Circuit opens, fails fast

4. **Scenario 4: Permanent Errors**
   - Authentication failures (401/403)
   - Tests no-retry logic
   - Expected: Immediate failure, no retries

5. **Scenario 5: Service Recovery**
   - Service fails then recovers
   - Tests circuit half-open state
   - Expected: Circuit closes after successful test

---
