#include <Arduino.h>
#include <Servo.h>


// MARK: Enum
enum class CapstanCommand {
  Up,
  Down,
  Stop,
  Help,
  Prznt,
  Invalid
};

// MARK: Declarations
const unsigned long COMMAND_TIMEOUT_MS = 10000;
unsigned long lastCommandTime = 0;

const size_t INPUT_BUFFER_SIZE = 16;
char inputBuffer[INPUT_BUFFER_SIZE];
size_t inputIndex = 0;

void printMenu();
void actuateUp();
void actuateDown();
void haltCapstan();
void presentWilson();
CapstanCommand parseCommand(const char *input);
void handleCommand(CapstanCommand cmd);
void readSerialCommand();
void sanitizeInput(char *input);

// 1000us = full reverse (-10.0 turns/s)
// 1500us = stop        (  0.0 turns/s)
// 2000us = full fwd    (+10.0 turns/s)
const int PWM_FULL_REV = 1000;
const int PWM_STOP     = 1500;
const int PWM_FULL_FWD = 2000;
const int PWM_PIN = 9;  // Servo library requires pin 9 or 10 on Uno

Servo capstanPWM;

// MARK: Setup
void setup() {
  Serial.begin(115200);
  delay(1000);

  capstanPWM.attach(PWM_PIN);
  capstanPWM.writeMicroseconds(PWM_STOP);

  Serial.println(F("Maintainer: Maison Gulyas"));
  Serial.println(F("Capstan Control System Testing"));

  printMenu();
  lastCommandTime = millis();
}

// MARK: Loop
void loop() {
  readSerialCommand();

  if (millis() - lastCommandTime > COMMAND_TIMEOUT_MS) {
    haltCapstan();
    lastCommandTime = millis();
  }
}

// MARK: Read Cmd
void readSerialCommand() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (inputIndex > 0) {
        inputBuffer[inputIndex] = '\0';
        sanitizeInput(inputBuffer);
        CapstanCommand cmd = parseCommand(inputBuffer);

        if (cmd == CapstanCommand::Invalid) {
          Serial.print(F("[INVALID] Unknown Command: "));
          Serial.println(inputBuffer);
          Serial.println(F("Valid Commands: w (up), x (down), s (stop), h (help)"));
        } else {
          handleCommand(cmd);
          lastCommandTime = millis();
        }
        inputIndex = 0;
      }
      return;
    }

    if (isPrintable(c)) {
      if (inputIndex < INPUT_BUFFER_SIZE - 1) {
        inputBuffer[inputIndex++] = c;
      } else {
        inputIndex = 0;
        Serial.println(F("[ERROR] Input too long. Command Cleared."));
      }
    }
  }
}

// MARK: Sanitization
void sanitizeInput(char *input) {
  for (size_t i = 0; input[i] != '\0'; i++) {
    input[i] = tolower(input[i]);
  }

  size_t start = 0;
  while (input[start] == ' ') start++;

  if (start > 0) {
    size_t i = 0;
    while (input[start] != '\0') input[i++] = input[start++];
    input[i] = '\0';
  }

  int end = strlen(input) - 1;
  while (end >= 0 && input[end] == ' ') input[end--] = '\0';
}

// MARK: Parse
CapstanCommand parseCommand(const char *input) {
  if (strcmp(input, "w") == 0 || strcmp(input, "up") == 0)   return CapstanCommand::Up;
  if (strcmp(input, "x") == 0 || strcmp(input, "down") == 0) return CapstanCommand::Down;
  if (strcmp(input, "s") == 0 || strcmp(input, "stop") == 0) return CapstanCommand::Stop;
  if (strcmp(input, "h") == 0 || strcmp(input, "help") == 0) return CapstanCommand::Help;
  if (strcmp(input, "p") == 0 || strcmp(input, "present") == 0) return CapstanCommand:: Prznt;
  return CapstanCommand::Invalid;
}

// MARK: Cmd Handler
void handleCommand(CapstanCommand cmd) {
  switch (cmd) {
    case CapstanCommand::Up:      actuateUp();   break;
    case CapstanCommand::Down:    actuateDown(); break;
    case CapstanCommand::Stop:    haltCapstan(); break;
    case CapstanCommand::Help:    printMenu();   break;
    case CapstanCommand::Prznt:   presentWilson(); break;
    case CapstanCommand::Invalid: break;
  }
}

// MARK: Menu
void printMenu() {
  const char *capstanMenu = R"MENU(
================================================
              CAPSTAN CONTROL TUI
================================================

                    [ W ]
                      |
                      |  UP
                      |
           [ S ] ---- + ---- [ H ]
            STOP              HELP
                      |
                      |  DOWN
                      |
                    [ X ]

------------------------------------------------
  Commands:
    w / up    Move capstan UP    (+10.0 turns/s)
    x / down  Move capstan DOWN  (-10.0 turns/s)
    s / stop  Stop capstan       (  0.0 turns/s)
    h / help  Show this menu
------------------------------------------------
  Status: READY
================================================
)MENU";
  Serial.print(capstanMenu);
}

// MARK: PWM Cmds
void actuateUp() {
  Serial.println(F("[CAPSTAN] Moving UP"));
  capstanPWM.writeMicroseconds(PWM_FULL_FWD);
}

void actuateDown() {
  Serial.println(F("[CAPSTAN] Moving DOWN"));
  capstanPWM.writeMicroseconds(PWM_FULL_REV);
}

void haltCapstan() {
  Serial.println(F("[CAPSTAN] STOP"));
  capstanPWM.writeMicroseconds(PWM_STOP);
}

void presentWilson() {

}