// vibration sensor config
struct VibrationSensor
{
    const uint8_t PIN;
    uint32_t numberKeyPresses;
    bool touched;
};

VibrationSensor vsensor1 = {18, 0, false};

// Interrupt service routine
// The ESP_INTR_FLAG_IRAM flag registers an interrupt handler that always runs
// from IRAM (and reads all its data from DRAM), and therefore does not need to be disabled
// during flash erase and write operations.
void IRAM_ATTR isr()
{
    vsensor1.numberKeyPresses += 1;
    vsensor1.touched = true;
}

void setup()
{
    Serial.begin(115200);
    pinMode(vsensor1.PIN, INPUT_PULLUP);
    attachInterrupt(vsensor1.PIN, isr, FALLING);
}

void loop()
{
    if (vsensor1.touched)
    {
        Serial.printf("VibrationSensor 1 has been touched %u times\n", vsensor1.numberKeyPresses);
        vsensor1.touched = false;
    }

    // Turn interrupt off after one minute
    static uint32_t lastMillis = 0;
    if (millis() - lastMillis > 60000)
    {
        lastMillis = millis();
        detachInterrupt(vsensor1.PIN);
        Serial.println("Interrupt Detached!");
    }
}