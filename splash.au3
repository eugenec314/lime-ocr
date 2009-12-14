#include <GDIPlus.au3>
#include <WindowsConstants.au3>
#include <GuiConstantsEx.au3>

Opt("MustDeclareVars", 1)
AutoItSetOption ("TrayIconHide", 1)

; ===============================================================================================================================
; Description ...: A simple splash screen to spice up Lime OCR Loading
; Usage..........: splash.exe time-in-seconds image title
; Example........: splash.exe 5 splash.png "We are loading ..."
; Author ........: Nishad TR, Lime Consultants [nishad at limeconsultants.com]
; License........: GNU GPL v3
; Version........: 0.3 a
; Notes .........: The images used for this demo MUST be 32 bpp with alpha channel for transparency
; Credits .......: Thanks to Paul Campbell (PaulIA) and lod3n 
; ===============================================================================================================================

; ===============================================================================================================================
; Global constants
; ===============================================================================================================================
Global Const $AC_SRC_ALPHA      = 1

; ===============================================================================================================================
; Global variables
; ===============================================================================================================================
Global $hGUI1, $hGUI2, $hImage, $SleepTimeFromCMD, $SplashIMG, $TitleFormCMD, $SleepTime

If $CmdLine[0] == 0 Then
	$SleepTimeFromCMD = 5
	$SplashIMG = "splash.png"
	$TitleFormCMD = "Loading ..."
EndIf

If $CmdLine[0] == 1 Then
	$SleepTimeFromCMD = $CmdLine[1]
	$SplashIMG = "splash.png"
	$TitleFormCMD = "Loading ..."
EndIf

If $CmdLine[0] == 2 Then
	$SleepTimeFromCMD = $CmdLine[1]
	$SplashIMG = $CmdLine[2]
	$TitleFormCMD = "Loading ..."
EndIf

If $CmdLine[0] == 3 Then
	$SleepTimeFromCMD = $CmdLine[1]
	$SplashIMG = $CmdLine[2]
	$TitleFormCMD = $CmdLine[3]
EndIf

; Create layered child window
$hGUI2 = GUICreate($TitleFormCMD, 250, 250, -1, -1, -1, $WS_EX_LAYERED+$WS_EX_TOPMOST, $hGUI1)

; Load layered image
_GDIPlus_Startup()
$hImage = _GDIPlus_ImageLoadFromFile(@ScriptDir & "\" & $SplashIMG)
SetBitMap($hGUI2, $hImage, 255)
GUISetState()

; Register notification messages
GUIRegisterMsg($WM_HSCROLL  , "WM_HSCROLL"  )
GUIRegisterMsg($WM_NCHITTEST, "WM_NCHITTEST")

; Loop until user exits
;do
;until GUIGetMsg() =$GUI_EVENT_CLOSE
$SleepTime = $SleepTimeFromCMD*1000
Sleep ($SleepTime)

; Release resources
_GDIPlus_ImageDispose($hImage)
_GDIPlus_Shutdown()

; ===============================================================================================================================
; Handle the WM_HSCROLL notificaton so that we can change the opacity in real time
; ===============================================================================================================================
Func WM_HSCROLL($hWnd, $iMsg, $iwParam, $ilParam)
  SetBitMap($hGUI2, $hImage, GUICtrlRead($iSlider))
EndFunc

; ===============================================================================================================================
; Handle the WM_NCHITTEST for the layered window so it can be dragged by clicking anywhere on the image.
; ===============================================================================================================================
Func WM_NCHITTEST($hWnd, $iMsg, $iwParam, $ilParam)
  if ($hWnd = $hGUI2) and ($iMsg = $WM_NCHITTEST) then Return $HTCAPTION
EndFunc

; ===============================================================================================================================
; SetBitMap
; ===============================================================================================================================
Func SetBitmap($hGUI, $hImage, $iOpacity)
  Local $hScrDC, $hMemDC, $hBitmap, $hOld, $pSize, $tSize, $pSource, $tSource, $pBlend, $tBlend

  $hScrDC  = _WinAPI_GetDC(0)
  $hMemDC  = _WinAPI_CreateCompatibleDC($hScrDC)
  $hBitmap = _GDIPlus_BitmapCreateHBITMAPFromBitmap($hImage)
  $hOld    = _WinAPI_SelectObject($hMemDC, $hBitmap)
  $tSize   = DllStructCreate($tagSIZE)
  $pSize   = DllStructGetPtr($tSize  )
  DllStructSetData($tSize, "X", _GDIPlus_ImageGetWidth ($hImage))
  DllStructSetData($tSize, "Y", _GDIPlus_ImageGetHeight($hImage))
  $tSource = DllStructCreate($tagPOINT)
  $pSource = DllStructGetPtr($tSource)
  $tBlend  = DllStructCreate($tagBLENDFUNCTION)
  $pBlend  = DllStructGetPtr($tBlend)
  DllStructSetData($tBlend, "Alpha" , $iOpacity    )
  DllStructSetData($tBlend, "Format", $AC_SRC_ALPHA)
  _WinAPI_UpdateLayeredWindow($hGUI, $hScrDC, 0, $pSize, $hMemDC, $pSource, 0, $pBlend, $ULW_ALPHA)
  _WinAPI_ReleaseDC   (0, $hScrDC)
  _WinAPI_SelectObject($hMemDC, $hOld)
  _WinAPI_DeleteObject($hBitmap)
  _WinAPI_DeleteDC    ($hMemDC)
EndFunc