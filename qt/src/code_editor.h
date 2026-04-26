#ifndef CODE_EDITOR_H
#define CODE_EDITOR_H

#include <QPlainTextEdit>
#include <QObject>

class QSyntaxHighlighter;

class CodeEditor : public QPlainTextEdit {
    Q_OBJECT

public:
    explicit CodeEditor(QWidget *parent = nullptr);

    void setLanguage(const QString &language);
    QString getCode() const;
    void setCode(const QString &code);

protected:
    void resizeEvent(QResizeEvent *event) override;

private slots:
    void updateLineNumberAreaWidth(int newBlockCount);
    void updateLineNumberArea(const QRect &rect, int dy);
    void highlightCurrentLine();

private:
    void setupLineNumbers();
    int lineNumberAreaWidth();
    void lineNumberAreaPaintEvent(QPaintEvent *event);

    QWidget *lineNumberArea;
    QSyntaxHighlighter *highlighter;
};

#endif // CODE_EDITOR_H
