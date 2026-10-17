/*
 * Minimal stand-in for the Windows SDK's EventToken.h.
 *
 * WebView2.h does `#include "EventToken.h"` but never references the EventToken
 * type itself, and MinGW-w64 (and any toolchain without the full Windows SDK on
 * the include path) does not ship that header. Declaring the opaque interface is
 * enough to compile; nothing here is ever called.
 */
#ifndef VOCA_EVENTTOKEN_H_STUB
#define VOCA_EVENTTOKEN_H_STUB

typedef struct IEventTokenVtbl IEventTokenVtbl;
typedef struct IEventToken {
    IEventTokenVtbl *lpVtbl;
} IEventToken, EventToken;

/* The Windows SDK declares this alongside EventToken; WebView2.h uses it in every
   add/remove event pair. Layout must match: a single 64-bit cookie. */
#ifndef __RUNTIMEEVENTREGISTRATIONTOKEN_DEFINED
#define __RUNTIMEEVENTREGISTRATIONTOKEN_DEFINED
typedef struct EventRegistrationToken {
    long long value;
} EventRegistrationToken;
#endif

struct IEventTokenVtbl {
    long (WINAPI *QueryInterface)(IEventToken *This, void *riid, void **ppvObject);
    unsigned long (WINAPI *AddRef)(IEventToken *This);
    unsigned long (WINAPI *Release)(IEventToken *This);
};

#endif /* VOCA_EVENTTOKEN_H_STUB */
