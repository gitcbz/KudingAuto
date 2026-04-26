#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTabWidget>
#include <QTextEdit>
#include <QLabel>
#include <memory>

class BackendClient;
class LoginTab;
class TestTab;
class ProblemTab;
class SettingsTab;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private:
    void setupUI();
    void setupConnections();
    void log(const QString &message);

    QTabWidget *tabWidget;
    QTextEdit *logText;
    QLabel *statusLabel;

    std::unique_ptr<BackendClient> backend;
    std::unique_ptr<LoginTab> loginTab;
    std::unique_ptr<TestTab> testTab;
    std::unique_ptr<ProblemTab> problemTab;
    std::unique_ptr<SettingsTab> settingsTab;

    friend class LoginTab;
    friend class TestTab;
    friend class ProblemTab;
    friend class SettingsTab;
};

#endif // MAINWINDOW_H
