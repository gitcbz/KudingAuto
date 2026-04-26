#include "mainwindow.h"
#include "backend_client.h"
#include "login_tab.h"
#include "test_tab.h"
#include "problem_tab.h"
#include "settings_tab.h"

#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QTextEdit>
#include <QPushButton>
#include <QLabel>
#include <QDateTime>
#include <QApplication>
#include <QStatusBar>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent) {
    setWindowTitle("Kuding Judge Helper v3.0");
    setGeometry(100, 100, 1000, 800);
    setMinimumSize(800, 600);

    // 创建后端客户端
    backend = std::make_unique<BackendClient>();

    setupUI();
    setupConnections();

    log("Application started");
    backend->checkStatus();
}

MainWindow::~MainWindow() = default;

void MainWindow::setupUI() {
    QWidget *centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);

    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);
    mainLayout->setContentsMargins(10, 10, 10, 10);
    mainLayout->setSpacing(8);

    // 标题
    QLabel *titleLabel = new QLabel("Kuding Judge Helper v3.0");
    titleLabel->setStyleSheet("font-size: 18px; font-weight: bold;");
    mainLayout->addWidget(titleLabel);

    // 标签页
    tabWidget = new QTabWidget();
    loginTab = std::make_unique<LoginTab>(backend.get());
    testTab = std::make_unique<TestTab>(backend.get());
    problemTab = std::make_unique<ProblemTab>(backend.get());
    settingsTab = std::make_unique<SettingsTab>(backend.get());

    tabWidget->addTab(loginTab.get(), "Login");
    tabWidget->addTab(testTab.get(), "Test Submit");
    tabWidget->addTab(problemTab.get(), "Problem Submit");
    tabWidget->addTab(settingsTab.get(), "Settings");

    mainLayout->addWidget(tabWidget, 1);

    // 日志区域
    QLabel *logLabel = new QLabel("Log");
    logLabel->setStyleSheet("font-weight: bold;");
    mainLayout->addWidget(logLabel);

    QHBoxLayout *logHeaderLayout = new QHBoxLayout();
    logHeaderLayout->addStretch();
    QPushButton *clearBtn = new QPushButton("Clear");
    clearBtn->setMaximumWidth(80);
    connect(clearBtn, &QPushButton::clicked, [this]() {
        logText->clear();
    });
    logHeaderLayout->addWidget(clearBtn);
    mainLayout->addLayout(logHeaderLayout);

    logText = new QTextEdit();
    logText->setReadOnly(true);
    logText->setMaximumHeight(120);
    logText->setStyleSheet("background-color: #2b2b2b; color: #ffffff; font-family: Courier;");
    mainLayout->addWidget(logText);

    // 状态栏
    statusLabel = new QLabel("Ready");
    statusBar()->addWidget(statusLabel);
}

void MainWindow::setupConnections() {
    connect(backend.get(), &BackendClient::error, this, [this](const QString &msg) {
        log("ERROR: " + msg);
    });
}

void MainWindow::log(const QString &message) {
    QString timestamp = QDateTime::currentDateTime().toString("hh:mm:ss");
    logText->append(QString("[%1] %2").arg(timestamp, message));
}
