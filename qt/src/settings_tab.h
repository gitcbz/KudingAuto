#ifndef SETTINGS_TAB_H
#define SETTINGS_TAB_H

#include <QWidget>
#include <QLineEdit>
#include <QCheckBox>
#include <QComboBox>

class BackendClient;

class SettingsTab : public QWidget {
    Q_OBJECT

public:
    explicit SettingsTab(BackendClient *backend, QWidget *parent = nullptr);

private slots:
    void onSaveSettings();
    void onDebugModeToggled(bool checked);
    void onLanguageChanged(const QString &language);
    void onOCRModeChanged(const QString &mode);

private:
    void setupUI();
    void loadSettings();

    BackendClient *backend;
    QLineEdit *apiUrlEdit;
    QCheckBox *debugModeCheck;
    QComboBox *languageCombo;
    QComboBox *ocrModeCombo;
};

#endif // SETTINGS_TAB_H
